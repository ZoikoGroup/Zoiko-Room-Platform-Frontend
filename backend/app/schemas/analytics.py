from app.schemas.common import CamelModel


class RevenueTrendPoint(CamelModel):
    month: str
    revenue: float
    bookings: int


class BookingsByTypePoint(CamelModel):
    type: str
    value: int


class OccupancyByCityPoint(CamelModel):
    city: str
    occupancy: int
