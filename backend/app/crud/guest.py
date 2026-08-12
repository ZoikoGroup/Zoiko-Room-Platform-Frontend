from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.booking import Booking
from app.models.guest import Guest
from app.schemas.guest import GuestRead


def list_guests(db: Session) -> list[GuestRead]:
    guests = db.scalars(select(Guest).options(joinedload(Guest.bookings).joinedload(Booking.listing)).order_by(Guest.name)).unique()
    return [to_guest_read(g) for g in guests]


def to_guest_read(guest: Guest) -> GuestRead:
    total_bookings = len(guest.bookings)
    total_spent = sum(b.total_amount for b in guest.bookings if b.payment_status == "paid")
    return GuestRead(
        id=guest.id,
        name=guest.name,
        email=guest.email,
        phone=guest.phone,
        avatar=guest.avatar,
        location=guest.location,
        total_bookings=total_bookings,
        total_spent=total_spent,
        joined_at=guest.joined_at,
        status=guest.status,
    )
