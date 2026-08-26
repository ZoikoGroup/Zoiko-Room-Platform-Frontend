from datetime import date

from sqlalchemy import Date, Index, String, UniqueConstraint
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

    bookings: Mapped[list["Booking"]] = relationship(back_populates="guest")
    reviews: Mapped[list["Review"]] = relationship(back_populates="guest")
