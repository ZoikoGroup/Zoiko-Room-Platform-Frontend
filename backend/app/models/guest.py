from datetime import date

from sqlalchemy import Date, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Guest(Base):
    __tablename__ = "guests"
    # 0001_initial.py created a table-level UNIQUE constraint on email plus a
    # separately named plain index (not a combined unique index) -- declared
    # explicitly here, matching the two real objects in the database, so
    # `alembic check` doesn't report a phantom constraint-vs-index diff.
    __table_args__ = (
        UniqueConstraint("email", name="guests_email_key"),
        Index("ix_guests_email", "email"),
    )

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), default="")
    avatar: Mapped[str] = mapped_column(String(1024), default="")
    location: Mapped[str] = mapped_column(String(255), default="")
    joined_at: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    # The real link to the self-service UserAccount this Guest represents, if
    # any -- replaces matching by `Guest.email == UserAccount.email` (fragile:
    # breaks silently if either email is later changed) as the source of truth
    # everywhere a "current user's guest record" is resolved. Nullable because
    # a Guest created through the legacy admin-only Booking flow (a walk-in
    # tenant with no self-service account) has nothing to link to. Unique so
    # one UserAccount maps to at most one Guest.
    user_account_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("user_accounts.id", ondelete="SET NULL"), unique=True, nullable=True
    )

    bookings: Mapped[list["Booking"]] = relationship(back_populates="guest")
    reviews: Mapped[list["Review"]] = relationship(back_populates="guest")
    user_account: Mapped["UserAccount"] = relationship()
