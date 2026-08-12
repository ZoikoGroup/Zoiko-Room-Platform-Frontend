from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

BOOKING_STATUSES = ("confirmed", "pending", "cancelled", "completed")
PAYMENT_STATUSES = ("paid", "unpaid", "refunded")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    listing_id: Mapped[str] = mapped_column(ForeignKey("listings.id"), nullable=False)
    guest_id: Mapped[str] = mapped_column(ForeignKey("guests.id"), nullable=False)
    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    guests: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    payment_status: Mapped[str] = mapped_column(String(20), default="unpaid")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    listing: Mapped["Listing"] = relationship(back_populates="bookings")
    guest: Mapped["Guest"] = relationship(back_populates="bookings")
    payment: Mapped["Payment"] = relationship(back_populates="booking", uselist=False)

    @property
    def nights(self) -> int:
        return max(1, (self.check_out - self.check_in).days)

    @property
    def total_amount(self) -> float:
        return self.nights * self.listing.price_per_night
