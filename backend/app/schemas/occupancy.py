from datetime import date, datetime

from app.schemas.common import CamelModel


class OccupancyRead(CamelModel):
    id: int
    offer_id: int
    listing_id: str
    room_id: int
    guest_id: str
    guest_name: str
    status: str
    move_in_date: date | None
    expected_end_date: date | None
    move_out_date: date | None
    created_at: datetime
    ended_at: datetime | None
