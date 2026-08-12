from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.booking import Booking
from app.models.payment import Payment
from app.schemas.payment import PaymentRead


def list_payments(db: Session) -> list[PaymentRead]:
    payments = db.scalars(
        select(Payment)
        .options(joinedload(Payment.booking).joinedload(Booking.guest), joinedload(Payment.booking).joinedload(Booking.listing))
        .order_by(Payment.date.desc())
    )
    return [to_payment_read(p) for p in payments]


def to_payment_read(payment: Payment) -> PaymentRead:
    return PaymentRead(
        id=payment.id,
        booking_id=payment.booking_id,
        guest_name=payment.booking.guest.name,
        amount=payment.booking.total_amount,
        method=payment.method,
        status=payment.status,
        date=payment.date,
    )
