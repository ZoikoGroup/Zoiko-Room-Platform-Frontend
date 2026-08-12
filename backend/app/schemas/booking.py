from datetime import date, datetime

from app.schemas.common import CamelModel


class NewGuestInput(CamelModel):
    name: str
    email: str
    phone: str = ""
    location: str = ""


class BookingCreate(CamelModel):
    listing_id: str
    guest_id: str | None = None
    new_guest: NewGuestInput | None = None
    check_in: date
    check_out: date
    guests: int
    status: str = "confirmed"
    payment_status: str = "unpaid"


class BookingRead(CamelModel):
    id: str
    listing_id: str
    listing_name: str
    property_type: str
    guest_name: str
    guest_email: str
    guest_avatar: str
    check_in: date
    check_out: date
    nights: int
    guests: int
    total_amount: float
    status: str
    payment_status: str
    created_at: datetime
