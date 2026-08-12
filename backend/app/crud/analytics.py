from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.listing import Listing
from app.schemas.analytics import BookingsByTypePoint, OccupancyByCityPoint, RevenueTrendPoint

PROPERTY_TYPE_LABELS = {
    "private_room": "Private Rooms",
}

# nights * price_per_night, computed in SQL since neither column is stored.
# Postgres `date - date` already yields an integer day count, so no date_part() needed.
_nights_expr = func.greatest(1, Booking.check_out - Booking.check_in)
_revenue_expr = _nights_expr * Listing.price_per_night


def revenue_trend(db: Session, months: int = 6) -> list[RevenueTrendPoint]:
    month_bucket = func.date_trunc("month", Booking.created_at)
    rows = db.execute(
        select(
            month_bucket.label("bucket"),
            func.sum(_revenue_expr).label("revenue"),
            func.count(Booking.id).label("bookings"),
        )
        .join(Listing, Listing.id == Booking.listing_id)
        .where(Booking.payment_status == "paid")
        .group_by("bucket")
        .order_by("bucket")
    ).all()
    return [
        RevenueTrendPoint(month=row.bucket.strftime("%b"), revenue=float(row.revenue or 0), bookings=row.bookings)
        for row in rows[-months:]
    ]


def bookings_by_type(db: Session) -> list[BookingsByTypePoint]:
    rows = db.execute(
        select(Listing.property_type, func.count(Booking.id).label("value"))
        .join(Listing, Listing.id == Booking.listing_id)
        .group_by(Listing.property_type)
        .order_by(func.count(Booking.id).desc())
    ).all()
    return [
        BookingsByTypePoint(type=PROPERTY_TYPE_LABELS.get(row.property_type, row.property_type), value=row.value)
        for row in rows
    ]


def occupancy_by_city(db: Session, limit: int = 6) -> list[OccupancyByCityPoint]:
    # No per-night room inventory/calendar table exists, so true occupancy (booked
    # nights / available nights) isn't computable. As a dynamic proxy we use active
    # bookings per listing in the city, capped at 100%, as a load indicator.
    active_statuses = ("confirmed", "pending", "completed")
    rows = db.execute(
        select(
            Listing.city,
            func.count(Booking.id).label("active_bookings"),
            func.count(func.distinct(Listing.id)).label("listing_count"),
        )
        .join(Booking, Booking.listing_id == Listing.id)
        .where(Booking.status.in_(active_statuses))
        .group_by(Listing.city)
        .order_by(func.count(Booking.id).desc())
        .limit(limit)
    ).all()
    return [
        OccupancyByCityPoint(
            city=row.city,
            occupancy=min(100, round(100 * row.active_bookings / max(1, row.listing_count))),
        )
        for row in rows
    ]
