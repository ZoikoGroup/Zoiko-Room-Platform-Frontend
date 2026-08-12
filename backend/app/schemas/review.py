from datetime import date

from app.schemas.common import CamelModel


class ReviewRead(CamelModel):
    id: str
    listing_id: str
    listing_name: str
    guest_name: str
    guest_avatar: str
    rating: int
    comment: str
    date: date
    property_type: str
