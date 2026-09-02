"""Tests for rental-application move-in-date validation (UAT batch #1, item 1).

A desired move-in date in the past must be rejected server-side, regardless of
what the frontend date picker allows -- this is the "cannot be bypassed by
calling the API directly" requirement.
"""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.identity_verification import IdentityVerification
from app.models.listing import Listing
from app.models.party import Party
from app.models.property import Property
from app.models.room import Room
from app.models.user_account import UserAccount
from tests.conftest import _make_user, auth_user_cookie


def _make_verified_renter_with_published_listing(db: Session, *, email: str = "renter@test.com") -> tuple[UserAccount, str]:
    """A USER with a verified identity, plus a PUBLISHED listing (owned by a
    different party) they're eligible to apply to. Returns (user, listing_id)."""
    renter_party = Party(party_type="renter", status="active", jurisdiction="IN")
    db.add(renter_party)
    db.flush()

    user = _make_user(db, email=email)
    user.party_id = renter_party.id
    db.flush()

    db.add(
        IdentityVerification(
            party_id=renter_party.id,
            document_type="passport",
            document_category="identity",
            status="verified",
        )
    )

    provider_party = Party(party_type="provider", status="active", jurisdiction="IN")
    db.add(provider_party)
    db.flush()

    prop = Property(owner_party_id=provider_party.id, address="1 Test St", city="Bengaluru", status="active")
    db.add(prop)
    db.flush()

    room = Room(property_id=prop.id, room_type="private_room", size=100, has_ensuite=True, status="active")
    db.add(room)
    db.flush()

    listing = Listing(
        id="L-APPTEST1",
        slug="apptest1",
        name="Test Listing",
        room_type="Private room",
        city="Bengaluru",
        location="Koramangala",
        price_per_night=500,
        guests=1,
        rating=4.5,
        review_count=0,
        party_id=provider_party.id,
        owner_id=None,
        room_id=room.id,
        state="PUBLISHED",
    )
    db.add(listing)
    db.commit()

    return user, listing.id


class TestMoveInDateValidation:
    def test_past_move_in_date_is_rejected(self, client, db_session: Session):
        user, listing_id = _make_verified_renter_with_published_listing(db_session)
        cookies = auth_user_cookie(user)
        past_date = (date.today() - timedelta(days=5)).isoformat()

        r = client.post(
            "/api/users/rentals/applications",
            json={"listingId": listing_id, "message": "hi", "desiredMoveIn": past_date},
            cookies=cookies,
        )
        assert r.status_code == 422, r.text
        assert "past" in r.text.lower()

    def test_todays_date_is_accepted(self, client, db_session: Session):
        user, listing_id = _make_verified_renter_with_published_listing(db_session, email="renter2@test.com")
        cookies = auth_user_cookie(user)
        today = date.today().isoformat()

        r = client.post(
            "/api/users/rentals/applications",
            json={"listingId": listing_id, "message": "hi", "desiredMoveIn": today},
            cookies=cookies,
        )
        assert r.status_code == 201, r.text
        assert r.json()["desiredMoveIn"] == today

    def test_future_date_is_accepted(self, client, db_session: Session):
        user, listing_id = _make_verified_renter_with_published_listing(db_session, email="renter3@test.com")
        cookies = auth_user_cookie(user)
        future_date = (date.today() + timedelta(days=30)).isoformat()

        r = client.post(
            "/api/users/rentals/applications",
            json={"listingId": listing_id, "message": "hi", "desiredMoveIn": future_date},
            cookies=cookies,
        )
        assert r.status_code == 201, r.text
        assert r.json()["desiredMoveIn"] == future_date
        assert r.json()["listingName"] == "Test Listing"

    def test_missing_move_in_date_still_allowed(self, client, db_session: Session):
        user, listing_id = _make_verified_renter_with_published_listing(db_session, email="renter4@test.com")
        cookies = auth_user_cookie(user)

        r = client.post(
            "/api/users/rentals/applications",
            json={"listingId": listing_id, "message": "no date given"},
            cookies=cookies,
        )
        assert r.status_code == 201, r.text
        assert r.json()["desiredMoveIn"] is None
