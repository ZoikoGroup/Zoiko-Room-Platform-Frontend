# NOTE: every function below combines the legacy short-stay Booking table
# with the real self-service rental lifecycle (SimulatedPayment for revenue,
# Occupancy for occupancy/bookings-by-type), so a renter who went through the
# actual Application -> Offer -> Agreement -> Occupancy flow shows up in these
# admin charts too, not just legacy admin-created bookings. Application rows
# are deliberately not counted here: they're not yet a completed rental or
# a confirmed payment, so including them would inflate "bookings"/"revenue"
# with unconfirmed activity.
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.finance import SimulatedPayment
from app.models.listing import Listing
from app.models.occupancy import Occupancy
from app.schemas.analytics import BookingsByTypePoint, OccupancyByCityPoint, RevenueTrendPoint

PROPERTY_TYPE_LABELS = {
    "private_room": "Private Rooms",
}

# nights * price_per_night, computed in SQL since neither column is stored.
# Postgres `date - date` already yields an integer day count, so no date_part() needed.
_nights_expr = func.greatest(1, Booking.check_out - Booking.check_in)
_revenue_expr = _nights_expr * Listing.price_per_night


def revenue_trend(db: Session, months: int = 6) -> list[RevenueTrendPoint]:
    """Merges legacy Booking revenue (nights * price, at booking creation
    time) with real rental-lifecycle revenue -- confirmed SimulatedPayments,
    at confirmation time -- bucketed by month."""
    buckets: dict[datetime, dict[str, float]] = {}

    def _add(bucket: datetime, revenue: float, events: int) -> None:
        entry = buckets.setdefault(bucket, {"revenue": 0.0, "events": 0})
        entry["revenue"] += revenue
        entry["events"] += events

    booking_month = func.date_trunc("month", Booking.created_at)
    booking_rows = db.execute(
        select(
            booking_month.label("bucket"),
            func.sum(_revenue_expr).label("revenue"),
            func.count(Booking.id).label("events"),
        )
        .join(Listing, Listing.id == Booking.listing_id)
        .where(Booking.payment_status == "paid")
        .group_by("bucket")
    ).all()
    for row in booking_rows:
        _add(row.bucket, float(row.revenue or 0), row.events)

    payment_month = func.date_trunc("month", SimulatedPayment.confirmed_at)
    payment_rows = db.execute(
        select(
            payment_month.label("bucket"),
            func.sum(SimulatedPayment.amount).label("revenue"),
            func.count(SimulatedPayment.id).label("events"),
        )
        .where(SimulatedPayment.status == "SUCCEEDED")
        .group_by("bucket")
    ).all()
    for row in payment_rows:
        _add(row.bucket, float(row.revenue or 0), row.events)

    ordered = sorted(buckets.items(), key=lambda kv: kv[0])
    return [
        RevenueTrendPoint(month=bucket.strftime("%b"), revenue=round(data["revenue"], 2), bookings=data["events"])
        for bucket, data in ordered[-months:]
    ]


def bookings_by_type(db: Session) -> list[BookingsByTypePoint]:
    """Combines legacy Booking counts with real Occupancy counts per listing
    property type -- a renter who went through the current lifecycle instead
    of the legacy admin Booking flow must count here too."""
    counts: dict[str, int] = {}

    booking_rows = db.execute(
        select(Listing.property_type, func.count(Booking.id).label("value"))
        .join(Listing, Listing.id == Booking.listing_id)
        .group_by(Listing.property_type)
    ).all()
    for row in booking_rows:
        counts[row.property_type] = counts.get(row.property_type, 0) + row.value

    occupancy_rows = db.execute(
        select(Listing.property_type, func.count(Occupancy.id).label("value"))
        .join(Listing, Listing.id == Occupancy.listing_id)
        .group_by(Listing.property_type)
    ).all()
    for row in occupancy_rows:
        counts[row.property_type] = counts.get(row.property_type, 0) + row.value

    return [
        BookingsByTypePoint(type=PROPERTY_TYPE_LABELS.get(property_type, property_type), value=value)
        for property_type, value in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    ]


def occupancy_by_city(db: Session, limit: int = 6) -> list[OccupancyByCityPoint]:
    # No per-night room inventory/calendar table exists, so true occupancy (booked
    # nights / available nights) isn't computable. As a dynamic proxy we use active
    # claims (legacy bookings + real occupancies) per engaged listing in the city,
    # capped at 100%, as a load indicator. Previously counted legacy Bookings only,
    # so a city rented entirely through the self-service flow reported 0%.
    active_booking_statuses = ("confirmed", "pending", "completed")
    active_occupancy_statuses = ("PENDING_MOVE_IN", "ACTIVE")

    active_count_by_city: dict[str, int] = {}
    engaged_listings_by_city: dict[str, set[str]] = {}

    def _record(listing_id: str, city: str) -> None:
        active_count_by_city[city] = active_count_by_city.get(city, 0) + 1
        engaged_listings_by_city.setdefault(city, set()).add(listing_id)

    booking_rows = db.execute(
        select(Listing.id, Listing.city)
        .join(Booking, Booking.listing_id == Listing.id)
        .where(Booking.status.in_(active_booking_statuses))
    ).all()
    for listing_id, city in booking_rows:
        _record(listing_id, city)

    occupancy_rows = db.execute(
        select(Listing.id, Listing.city)
        .join(Occupancy, Occupancy.listing_id == Listing.id)
        .where(Occupancy.status.in_(active_occupancy_statuses))
    ).all()
    for listing_id, city in occupancy_rows:
        _record(listing_id, city)

    ranked = sorted(active_count_by_city.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    return [
        OccupancyByCityPoint(
            city=city,
            occupancy=min(100, round(100 * active_count / max(1, len(engaged_listings_by_city[city])))),
        )
        for city, active_count in ranked
    ]
