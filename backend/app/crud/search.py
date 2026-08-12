from urllib.parse import quote

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.admin_user import AdminUser
from app.models.booking import Booking
from app.models.guest import Guest
from app.models.listing import Listing
from app.schemas.search import SearchResult

RESULT_LIMIT = 5


def global_search(db: Session, admin: AdminUser, query: str) -> list[SearchResult]:
    like = f"%{query}%"
    results: list[SearchResult] = []

    listing_query = select(Listing).where(or_(Listing.name.ilike(like), Listing.city.ilike(like)))
    if admin.role != "super_admin":
        listing_query = listing_query.where(Listing.owner_id == admin.id)
    listings = db.scalars(listing_query.limit(RESULT_LIMIT))
    for listing in listings:
        results.append(
            SearchResult(
                id=listing.id,
                type="listing",
                title=listing.name,
                subtitle=f"{listing.city} · {listing.room_type}",
                href=f"/properties?q={quote(listing.name)}",
            )
        )

    if admin.role == "super_admin":
        guests = db.scalars(
            select(Guest).where(or_(Guest.name.ilike(like), Guest.email.ilike(like))).limit(RESULT_LIMIT)
        )
        for guest in guests:
            results.append(
                SearchResult(
                    id=guest.id,
                    type="guest",
                    title=guest.name,
                    subtitle=guest.email,
                    href=f"/guests?q={quote(guest.name)}",
                )
            )

        bookings = db.scalars(
            select(Booking)
            .options(joinedload(Booking.guest), joinedload(Booking.listing))
            .join(Guest, Booking.guest_id == Guest.id)
            .join(Listing, Booking.listing_id == Listing.id)
            .where(or_(Booking.id.ilike(like), Guest.name.ilike(like), Listing.name.ilike(like)))
            .limit(RESULT_LIMIT)
        )
        for booking in bookings:
            results.append(
                SearchResult(
                    id=booking.id,
                    type="booking",
                    title=f"{booking.guest.name} — {booking.listing.name}",
                    subtitle=f"Booking {booking.id}",
                    href=f"/bookings?q={quote(booking.id)}",
                )
            )

    return results
