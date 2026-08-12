from datetime import date

from app.schemas.common import CamelModel


class GuestRead(CamelModel):
    id: str
    name: str
    email: str
    phone: str
    avatar: str
    location: str
    total_bookings: int
    total_spent: float
    joined_at: date
    status: str
