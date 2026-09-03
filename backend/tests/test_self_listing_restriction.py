"""Tests for UAT batch #2, item 2: a host must not see or be able to apply to
their own hosted listing, and this must hold even calling the API directly.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.identity_verification import IdentityVerification
from app.models.listing import Listing
from app.models.party import Party
from app.models.property import Property
from app.models.room import Room
from app.models.user_account import UserAccount
from tests.conftest import _make_user, auth_user_cookie


def _make_host_and_listing(db: Session, *, email: str = "host@test.com") -> tuple[UserAccount, str]:
    """A USER hosting a PUBLISHED listing through their own party, with a verified
    identity (so identity verification never blocks the self-application check
    from being reached). Returns (host_user, listing_id)."""
    provider_party = Party(party_type="provider", status="active", jurisdiction="IN")
    db.add(provider_party)
    db.flush()

    host = _make_user(db, email=email)
    host.party_id = provider_party.id
    db.flush()

    db.add(
        IdentityVerification(
            party_id=provider_party.id,
            document_type="passport",
            document_category="identity",
            status="verified",
        )
    )

    prop = Property(owner_party_id=provider_party.id, address="1 Host St", city="Bengaluru", status="active")
    db.add(prop)
    db.flush()

    room = Room(property_id=prop.id, room_type="private_room", size=120, has_ensuite=True, status="active")
    db.add(room)
    db.flush()

    listing = Listing(
        id="L-SELFTEST1",
        slug="selftest1",
        name="Host's Own Room",
        room_type="Private room",
        city="Bengaluru",
        location="Indiranagar",
        price_per_night=700,
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

    return host, listing.id


def _make_verified_renter(db: Session, *, email: str = "otherrenter@test.com") -> UserAccount:
    renter_party = Party(party_type="renter", status="active", jurisdiction="IN")
    db.add(renter_party)
    db.flush()

    renter = _make_user(db, email=email)
    renter.party_id = renter_party.id
    db.flush()

    db.add(
        IdentityVerification(
            party_id=renter_party.id,
            document_type="passport",
            document_category="identity",
            status="verified",
        )
    )
    db.commit()
    return renter


class TestSelfApplicationBlocked:
    def test_owner_cannot_apply_to_own_listing(self, client, db_session: Session):
        host, listing_id = _make_host_and_listing(db_session)
        cookies = auth_user_cookie(host)

        r = client.post(
            "/api/users/rentals/applications",
            json={"listingId": listing_id, "message": "I'd like to rent my own room"},
            cookies=cookies,
        )
        assert r.status_code == 403, r.text
        assert "own listing" in r.text.lower()

    def test_another_user_can_apply(self, client, db_session: Session):
        _host, listing_id = _make_host_and_listing(db_session)
        renter = _make_verified_renter(db_session)
        cookies = auth_user_cookie(renter)

        r = client.post(
            "/api/users/rentals/applications",
            json={"listingId": listing_id, "message": "Interested in this room"},
            cookies=cookies,
        )
        assert r.status_code == 201, r.text
        assert r.json()["listingId"] == listing_id


class TestSelfListingExcludedFromPublicSearch:
    def test_own_listing_excluded_from_search_results(self, client, db_session: Session):
        host, listing_id = _make_host_and_listing(db_session, email="host2@test.com")
        cookies = auth_user_cookie(host)

        r = client.get("/api/public/listings", cookies=cookies)
        assert r.status_code == 200, r.text
        ids = [item["id"] for item in r.json()["items"]]
        assert listing_id not in ids

    def test_own_listing_detail_returns_404_for_owner(self, client, db_session: Session):
        host, listing_id = _make_host_and_listing(db_session, email="host3@test.com")
        cookies = auth_user_cookie(host)

        r = client.get(f"/api/public/listings/{listing_id}", cookies=cookies)
        assert r.status_code == 404, r.text

    def test_listing_visible_to_other_users_and_unauthenticated_callers(self, client, db_session: Session):
        _host, listing_id = _make_host_and_listing(db_session, email="host4@test.com")
        renter = _make_verified_renter(db_session, email="otherrenter2@test.com")
        cookies = auth_user_cookie(renter)

        r = client.get("/api/public/listings", cookies=cookies)
        assert r.status_code == 200, r.text
        assert listing_id in [item["id"] for item in r.json()["items"]]

        r_detail = client.get(f"/api/public/listings/{listing_id}", cookies=cookies)
        assert r_detail.status_code == 200, r_detail.text

        # No cookie at all -- the unauthenticated renter-facing path -- must still work.
        r_anon = client.get("/api/public/listings")
        assert r_anon.status_code == 200, r_anon.text
        assert listing_id in [item["id"] for item in r_anon.json()["items"]]

        r_anon_detail = client.get(f"/api/public/listings/{listing_id}")
        assert r_anon_detail.status_code == 200, r_anon_detail.text
