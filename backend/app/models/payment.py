from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

PAYMENT_METHODS = ("Credit Card", "UPI", "Net Banking", "PayPal", "Wallet")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    booking_id: Mapped[str] = mapped_column(ForeignKey("bookings.id"), unique=True, nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    booking: Mapped["Booking"] = relationship(back_populates="payment")
