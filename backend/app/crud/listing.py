from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.crud.authority import get_valid_authority_for_room
from app.crud.ids import new_id, slugify
from app.crud.identity_verification import get_verified_identity_for_party
from app.crud.occupancy_classification import get_classification_for_room
from app.models.admin_user import AdminUser
from app.models.listing import Listing
from app.models.market_release import MarketRelease
from app.models.room import Room
from app.schemas.listing import ListingCreate, ListingUpdate, PublicListingRead


def _resolve_market_release_id_for_room(db: Session, room_id: int | None) -> int | None:
    """A listing's market is derived from its room's owning party's jurisdiction --
    never hand-picked by the provider, so a listing can't be steered toward a more
    permissive market than the one it actually operates in."""
    if room_id is None:
        return None
    room = db.get(Room, room_id)
    if room is None:
        return None
    jurisdiction = room.property.owner_party.jurisdiction
    release = db.scalar(select(MarketRelease).where(MarketRelease.jurisdiction == jurisdiction))
    return release.id if release else None


def list_listings_for(db: Session, admin: AdminUser) -> list[Listing]:
    query = select(Listing).order_by(Listing.name)
    if admin.role != "super_admin":
        query = query.where(Listing.owner_id == admin.id)
    return list(db.scalars(query))


def list_public_listings(db: Session) -> list[Listing]:
    query = (
        select(Listing)
        .options(joinedload(Listing.owner))
        .where(Listing.state == "PUBLISHED")
        .order_by(Listing.name)
    )
    return list(db.scalars(query))


def get_listing(db: Session, listing_id: str) -> Listing | None:
    return db.get(Listing, listing_id)


def to_public_listing_read(listing: Listing) -> PublicListingRead:
    return PublicListingRead(
        id=listing.id,
        slug=listing.slug,
        name=listing.name,
        property_type=listing.property_type,
        room_type=listing.room_type,
        city=listing.city,
        location=listing.location,
        latitude=listing.latitude,
        longitude=listing.longitude,
        price_per_night=listing.price_per_night,
        rating=listing.rating,
        review_count=listing.review_count,
        guests=listing.guests,
        bedrooms=listing.bedrooms,
        bathrooms=listing.bathrooms,
        size=listing.size,
        images=listing.images,
        amenities=listing.amenities,
        tags=listing.tags,
        description=listing.description,
        featured=listing.featured,
        room_id=listing.room_id,
        min_stay_nights=listing.min_stay_nights,
        owner_name=listing.contact_name or (listing.owner.full_name if listing.owner else "Host"),
        owner_email=listing.contact_email or (listing.owner.email if listing.owner else ""),
        owner_phone=listing.contact_phone or (listing.owner.phone if listing.owner else ""),
    )


def create_listing(db: Session, data: ListingCreate, owner: AdminUser) -> Listing:
    if data.min_stay_nights < 30:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Minimum stay must be at least 30 nights")

    listing = Listing(
        id=new_id("L"),
        slug=slugify(data.name),
        rating=4.5,
        review_count=0,
        owner_id=owner.id,
        state="DRAFT",
        market_release_id=_resolve_market_release_id_for_room(db, data.room_id),
        **data.model_dump(),
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def create_listing_for_party(db: Session, data: ListingCreate, party_id: int) -> Listing:
    """Create a USER-hosted draft listing without requiring an AdminUser."""
    if data.min_stay_nights < 30:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Minimum stay must be at least 30 nights")
    if data.room_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A hosted listing must be linked to one of your rooms")

    assert_party_owns_room(db, data.room_id, party_id)
    listing = Listing(
        id=new_id("L"), slug=slugify(data.name), rating=4.5, review_count=0,
        owner_id=None, party_id=party_id, state="DRAFT",
        market_release_id=_resolve_market_release_id_for_room(db, data.room_id),
        **data.model_dump(),
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def assert_party_owns_listing(listing: Listing, party_id: int) -> None:
    if listing.party_id != party_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only manage listings owned by your party")


def assert_party_owns_room(db: Session, room_id: int, party_id: int) -> None:
    room = db.get(Room, room_id)
    if not room or room.property.owner_party_id != party_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only list rooms owned by your party")


def update_listing(db: Session, listing: Listing, data: ListingUpdate) -> Listing:
    if data.min_stay_nights is not None and data.min_stay_nights < 30:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Minimum stay must be at least 30 nights")

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(listing, field, value)
    if "room_id" in updates:
        listing.market_release_id = _resolve_market_release_id_for_room(db, listing.room_id)
    db.commit()
    db.refresh(listing)
    return listing


def delete_listing(db: Session, listing: Listing) -> None:
    db.delete(listing)
    db.commit()


def duplicate_listing(db: Session, listing: Listing, owner: AdminUser) -> Listing:
    copy = Listing(
        id=new_id("L"),
        slug=f"{listing.slug}-copy-{new_id('').lower().lstrip('-')}",
        name=f"{listing.name} (Copy)",
        property_type=listing.property_type,
        room_type=listing.room_type,
        city=listing.city,
        location=listing.location,
        latitude=listing.latitude,
        longitude=listing.longitude,
        price_per_night=listing.price_per_night,
        rating=listing.rating,
        review_count=0,
        guests=listing.guests,
        bedrooms=listing.bedrooms,
        bathrooms=listing.bathrooms,
        size=listing.size,
        images=list(listing.images),
        amenities=list(listing.amenities),
        tags=list(listing.tags),
        description=listing.description,
        featured=False,
        room_id=listing.room_id,
        min_stay_nights=listing.min_stay_nights,
        market_release_id=listing.market_release_id,
        contact_name=listing.contact_name,
        contact_phone=listing.contact_phone,
        contact_email=listing.contact_email,
        owner_id=owner.id,
        state="DRAFT",
    )
    db.add(copy)
    db.commit()
    db.refresh(copy)
    return copy


def set_listing_state(db: Session, listing: Listing, state: str) -> Listing:
    listing.state = state
    db.commit()
    db.refresh(listing)
    return listing


def check_publish_eligibility(db: Session, listing: Listing) -> list[str]:
    """Fail-closed eligibility gate. Returns a list of blocking reasons -- empty means
    the listing may publish. Every check runs regardless of who owns the listing;
    identity/role is never treated as proof of authority."""
    reasons: list[str] = []

    if listing.room_id is None:
        reasons.append("Listing is not linked to a room")
        return reasons

    if listing.min_stay_nights < 30:
        reasons.append("Minimum stay must be at least 30 nights")

    market_release = db.get(MarketRelease, listing.market_release_id) if listing.market_release_id else None
    if not market_release or market_release.status != "active":
        reasons.append("No active market release for this listing")
    elif listing.min_stay_nights < market_release.min_stay_nights:
        reasons.append(f"Minimum stay must be at least {market_release.min_stay_nights} nights for this market")

    authority = get_valid_authority_for_room(db, listing.room_id)
    if not authority:
        reasons.append("No verified, unexpired authority record for this room")

    classification = get_classification_for_room(db, listing.room_id)
    if not classification or classification.review_state in ("UNKNOWN", "UNSUPPORTED"):
        reasons.append("Occupancy classification is missing or unresolved")

    provider_party_id = listing.room.property.owner_party_id
    identity = get_verified_identity_for_party(db, provider_party_id)
    if not identity:
        reasons.append("Provider identity verification is not approved")

    return reasons


def publish_listing(db: Session, listing: Listing) -> Listing:
    reasons = check_publish_eligibility(db, listing)
    if reasons:
        raise HTTPException(status.HTTP_409_CONFLICT, {"message": "Listing is not eligible to publish", "reasons": reasons})
    return set_listing_state(db, listing, "PUBLISHED")
