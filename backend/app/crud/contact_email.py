from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.contact_email import ContactEmail


def create_contact_email(db: Session, user_id: int, subject: str, message: str) -> ContactEmail:
    email = ContactEmail(user_id=user_id, subject=subject, message=message)
    db.add(email)
    db.commit()
    db.refresh(email)
    return email


def list_contact_emails(db: Session, unread_only: bool = False) -> list[ContactEmail]:
    stmt = (
        select(ContactEmail)
        .options(joinedload(ContactEmail.user))
        .order_by(ContactEmail.created_at.desc())
    )
    if unread_only:
        stmt = stmt.where(ContactEmail.is_read == False)  # noqa: E712
    return list(db.scalars(stmt.limit(50)))


def get_contact_email(db: Session, email_id: int) -> ContactEmail | None:
    return db.get(ContactEmail, email_id)


def mark_contact_email_read(db: Session, email_id: int) -> ContactEmail | None:
    email = db.get(ContactEmail, email_id)
    if email:
        email.is_read = True
        db.commit()
        db.refresh(email)
    return email


def count_unread_contact_emails(db: Session) -> int:
    from sqlalchemy import func

    return db.scalar(select(func.count()).select_from(ContactEmail).where(ContactEmail.is_read == False)) or 0  # noqa: E712
