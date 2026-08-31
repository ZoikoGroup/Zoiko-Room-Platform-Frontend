from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Exactly one of recipient_user_id / recipient_admin_id is set per row -- a
# notification always targets one concrete recipient. "Notify all super admins"
# events fan out into one row per super admin at creation time rather than a
# broadcast row read at query time, so each recipient's read state is independent
# and the read/list queries stay a single indexed lookup.
RECIPIENT_TYPES = ("user", "admin")


class Notification(Base):
    __tablename__ = "notifications"
    # Prevents the exact same event from notifying the exact same recipient twice
    # (e.g. a double-submitted approve click). Postgres unique constraints never
    # treat two NULLs as equal, so a constraint built directly on the two nullable
    # recipient_user_id/recipient_admin_id columns would silently never fire --
    # exactly one of them is always NULL. recipient_key is a non-nullable
    # "user:<id>" / "admin:<id>" string computed at insert time (see
    # crud/notification.py) specifically so this constraint has no NULL column to
    # dodge past.
    __table_args__ = (
        UniqueConstraint(
            "notification_type", "related_entity_type", "related_entity_id", "recipient_key",
            name="uq_notifications_dedupe",
        ),
        Index("ix_notifications_recipient_user", "recipient_user_id", "is_read"),
        Index("ix_notifications_recipient_admin", "recipient_admin_id", "is_read"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_type: Mapped[str] = mapped_column(String(10), nullable=False)
    recipient_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=True
    )
    recipient_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=True
    )
    recipient_key: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(2000), default="")
    notification_type: Mapped[str] = mapped_column(String(100), nullable=False)
    related_entity_type: Mapped[str] = mapped_column(String(50), default="")
    related_entity_id: Mapped[str] = mapped_column(String(50), default="")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    recipient_user: Mapped["UserAccount"] = relationship()
    recipient_admin: Mapped["AdminUser"] = relationship()
