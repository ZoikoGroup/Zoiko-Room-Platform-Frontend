from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.leasing import submit_application, to_application_read
from app.crud.listing import get_listing, list_public_listings, to_public_listing_read
from app.db.session import get_db
from app.schemas.leasing import ApplicationCreate, ApplicationRead
from app.schemas.listing import PublicListingRead, PublicListingsPage

router = APIRouter(prefix="/api/public", tags=["public"])

MAX_PUBLIC_LISTINGS_LIMIT = 100


@router.get("/listings", response_model=PublicListingsPage)
def get_public_listings(
    city: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    room_type: str | None = None,
    amenities: str | None = Query(default=None, description="Comma-separated list of required amenities"),
    limit: int = Query(default=20, ge=1, le=MAX_PUBLIC_LISTINGS_LIMIT),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    amenity_list = [a.strip() for a in amenities.split(",") if a.strip()] if amenities else None
    listings, total = list_public_listings(
        db,
        city=city,
        min_price=min_price,
        max_price=max_price,
        room_type=room_type,
        amenities=amenity_list,
        limit=limit,
        offset=offset,
    )
    return PublicListingsPage(
        items=[to_public_listing_read(listing) for listing in listings],
        limit=limit,
        offset=offset,
        total=total,
        has_more=offset + len(listings) < total,
    )


@router.get("/listings/{listing_id}", response_model=PublicListingRead)
def get_public_listing(listing_id: str, db: Session = Depends(get_db)):
    """Single-listing detail view. Same visibility rule as the list endpoint --
    only ever returns a PUBLISHED listing, so a draft/paused/withdrawn listing
    is never reachable by guessing its id."""
    listing = get_listing(db, listing_id)
    if not listing or listing.state != "PUBLISHED":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Listing not found")
    return to_public_listing_read(listing)


@router.post("/applications", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def post_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    """No auth -- the separate renter-facing website submits directly on a renter's
    behalf, same as the existing new-guest booking flow."""
    return to_application_read(submit_application(db, payload))
