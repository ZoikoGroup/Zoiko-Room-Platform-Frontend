# NOTE: also indexes the real rental-lifecycle records (Application,
# Occupancy) alongside the legacy Booking/Guest tables, so a renter who went
# through the current self-service flow is findable here too, not just
# legacy admin-created bookings. UserAccount itself is deliberately NOT a
# separate result type: there is no admin page to list/find a UserAccount by
# id, so a "user" result would be a dead link -- out of scope to build one
# here (see AGENTS.md: don't invent frontend features while closing a
# backend gap).
from urllib.parse import quote

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.admin_user import AdminUser
from app.models.booking import Booking
from app.models.guest import Guest
from app.models.leasing import Application
from app.models.listing import Listing
from app.models.occupancy import Occupancy
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

        applications = db.scalars(
            select(Application)
            .options(joinedload(Application.guest), joinedload(Application.listing))
            .join(Guest, Application.guest_id == Guest.id)
            .join(Listing, Application.listing_id == Listing.id)
            .where(or_(Guest.name.ilike(like), Guest.email.ilike(like), Listing.name.ilike(like)))
            .limit(RESULT_LIMIT)
        )
        for application in applications:
            results.append(
                SearchResult(
                    id=str(application.id),
                    type="application",
                    title=f"{application.guest.name} — {application.listing.name}",
                    subtitle=f"Application #{application.id} · {application.status}",
                    href=f"/leasing?q={quote(application.guest.name)}",
                )
            )

        occupancies = db.scalars(
            select(Occupancy)
            .options(joinedload(Occupancy.guest), joinedload(Occupancy.listing))
            .join(Guest, Occupancy.guest_id == Guest.id)
            .join(Listing, Occupancy.listing_id == Listing.id)
            .where(or_(Guest.name.ilike(like), Guest.email.ilike(like), Listing.name.ilike(like)))
            .limit(RESULT_LIMIT)
        )
        for occupancy in occupancies:
            results.append(
                SearchResult(
                    id=str(occupancy.id),
                    type="occupancy",
                    title=f"{occupancy.guest.name} — {occupancy.listing.name}",
                    subtitle=f"Occupancy #{occupancy.id} · {occupancy.status}",
                    href=f"/occupancy?q={quote(occupancy.guest.name)}",
                )
            )

    return results
