from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.admin_user import AdminUser
from app.models.notification import Notification
from app.models.user_account import UserAccount


def _create(
    db: Session,
    *,
    recipient_type: str,
    recipient_user_id: int | None,
    recipient_admin_id: int | None,
    title: str,
    message: str,
    notification_type: str,
    related_entity_type: str,
    related_entity_id: str,
) -> Notification | None:
    """Creates one notification row, silently no-op on an exact duplicate (same
    type/entity/recipient -- see the model's unique constraint) instead of
    raising. Runs in a SAVEPOINT so a duplicate never aborts the caller's outer
    transaction, which is why this is always called well before the caller's
    own db.commit()."""
    recipient_key = f"user:{recipient_user_id}" if recipient_type == "user" else f"admin:{recipient_admin_id}"
    notification = Notification(
        recipient_type=recipient_type,
        recipient_user_id=recipient_user_id,
        recipient_admin_id=recipient_admin_id,
        recipient_key=recipient_key,
        title=title,
        message=message,
        notification_type=notification_type,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
    )
    try:
        with db.begin_nested():
            db.add(notification)
            db.flush()
    except IntegrityError:
        return None
    return notification


def notify_user(
    db: Session, user_id: int, *, title: str, message: str, notification_type: str,
    related_entity_type: str = "", related_entity_id: str = "",
) -> Notification | None:
    return _create(
        db, recipient_type="user", recipient_user_id=user_id, recipient_admin_id=None,
        title=title, message=message, notification_type=notification_type,
        related_entity_type=related_entity_type, related_entity_id=related_entity_id,
    )


def notify_user_by_party(db: Session, party_id: int | None, **kwargs) -> Notification | None:
    """Looks up the active UserAccount for a party -- the same party_id ->
    UserAccount lookup already used across hosting/sublet crud -- and notifies
    them. No-ops silently if the party has no user account (e.g. it's an
    admin-owned party, which has nobody on the USER side to notify)."""
    if not party_id:
        return None
    user = db.scalar(
        select(UserAccount).where(UserAccount.party_id == party_id, UserAccount.is_active.is_(True))
    )
    if not user:
        return None
    return notify_user(db, user.id, **kwargs)


def notify_user_by_guest_email(db: Session, guest_email: str, **kwargs) -> Notification | None:
    """Looks up the UserAccount linked to a Guest record by email -- the same
    Guest<->UserAccount link already used across the rentals/sublet flows."""
    user = db.scalar(select(UserAccount).where(UserAccount.email == guest_email))
    if not user:
        return None
    return notify_user(db, user.id, **kwargs)


def notify_admin(
    db: Session, admin_id: int, *, title: str, message: str, notification_type: str,
    related_entity_type: str = "", related_entity_id: str = "",
) -> Notification | None:
    return _create(
        db, recipient_type="admin", recipient_user_id=None, recipient_admin_id=admin_id,
        title=title, message=message, notification_type=notification_type,
        related_entity_type=related_entity_type, related_entity_id=related_entity_id,
    )


def notify_all_super_admins(db: Session, **kwargs) -> list[Notification]:
    """Fans out into one row per active super admin so each has an independent
    read state -- see the model docstring for why this isn't a single broadcast row."""
    admin_ids = db.scalars(
        select(AdminUser.id).where(AdminUser.role == "super_admin", AdminUser.is_active.is_(True))
    )
    created = []
    for admin_id in admin_ids:
        row = notify_admin(db, admin_id, **kwargs)
        if row:
            created.append(row)
    return created


def notify_all_admins(db: Session, **kwargs) -> list[Notification]:
    """Same fan-out as notify_all_super_admins, but every active admin regardless
    of role -- for operational events (e.g. a listing submitted for review) that
    any admin, not just super admins, should see and can act on."""
    admin_ids = db.scalars(
        select(AdminUser.id).where(AdminUser.is_active.is_(True), AdminUser.approval_status == "approved")
    )
    created = []
    for admin_id in admin_ids:
        row = notify_admin(db, admin_id, **kwargs)
        if row:
            created.append(row)
    return created


def list_for_user(db: Session, user_id: int, limit: int = 50) -> list[Notification]:
    return list(
        db.scalars(
            select(Notification)
            .where(Notification.recipient_user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
    )


def list_for_admin(db: Session, admin_id: int, limit: int = 50) -> list[Notification]:
    return list(
        db.scalars(
            select(Notification)
            .where(Notification.recipient_admin_id == admin_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
    )


def count_unread_for_user(db: Session, user_id: int) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.recipient_user_id == user_id, Notification.is_read.is_(False))
        )
        or 0
    )


def count_unread_for_admin(db: Session, admin_id: int) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.recipient_admin_id == admin_id, Notification.is_read.is_(False))
        )
        or 0
    )


def mark_read_for_user(db: Session, notification_id: int, user_id: int) -> Notification | None:
    """Scoped to the caller's own user_id -- a USER can never mark (or even
    address) another USER's notification, regardless of what id is requested."""
    notification = db.scalar(
        select(Notification).where(Notification.id == notification_id, Notification.recipient_user_id == user_id)
    )
    if not notification:
        return None
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
    return notification


def mark_read_for_admin(db: Session, notification_id: int, admin_id: int) -> Notification | None:
    """Scoped to the caller's own admin_id -- one admin can never mark another
    admin's notification, super admin included."""
    notification = db.scalar(
        select(Notification).where(Notification.id == notification_id, Notification.recipient_admin_id == admin_id)
    )
    if not notification:
        return None
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
    return notification


def mark_all_read_for_user(db: Session, user_id: int) -> int:
    now = datetime.now(timezone.utc)
    result = db.execute(
        select(Notification).where(Notification.recipient_user_id == user_id, Notification.is_read.is_(False))
    )
    rows = list(result.scalars())
    for row in rows:
        row.is_read = True
        row.read_at = now
    db.commit()
    return len(rows)


def mark_all_read_for_admin(db: Session, admin_id: int) -> int:
    now = datetime.now(timezone.utc)
    result = db.execute(
        select(Notification).where(Notification.recipient_admin_id == admin_id, Notification.is_read.is_(False))
    )
    rows = list(result.scalars())
    for row in rows:
        row.is_read = True
        row.read_at = now
    db.commit()
    return len(rows)
