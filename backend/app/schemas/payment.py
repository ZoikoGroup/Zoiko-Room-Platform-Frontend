from datetime import date

from app.schemas.common import CamelModel


class PaymentRead(CamelModel):
    id: str
    booking_id: str
    guest_name: str
    amount: float
    method: str
    status: str
    date: date
