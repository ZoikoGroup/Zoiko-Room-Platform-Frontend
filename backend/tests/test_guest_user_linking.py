"""Unit tests for the Guest<->UserAccount FK (crud/guest.py) that replaced
matching by `Guest.email == UserAccount.email` string comparison everywhere a
"current user's guest record" was resolved -- the fragile pattern the Anil
task list flagged for section 4 (rental lifecycle source of truth).
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.guest import get_guest_for_user, get_or_create_guest_for_user
from app.crud.notification import notify_user_by_guest
from app.models.guest import Guest
from app.models.notification import Notification
from tests.conftest import _make_user


class TestGetOrCreateGuestForUser:
    def test_first_call_creates_a_linked_guest(self, db_session: Session):
        user = _make_user(db_session, email="new@test.com")

        guest = get_or_create_guest_for_user(db_session, user)
        db_session.commit()

        assert guest.user_account_id == user.id
        assert guest.email == user.email

    def test_second_call_returns_the_same_guest_not_a_duplicate(self, db_session: Session):
        user = _make_user(db_session, email="repeat@test.com")

        first = get_or_create_guest_for_user(db_session, user)
        db_session.commit()
        second = get_or_create_guest_for_user(db_session, user)
        db_session.commit()

        assert first.id == second.id
        count = db_session.scalar(select(Guest).where(Guest.user_account_id == user.id))
        assert count is not None


class TestGetGuestForUser:
    def test_finds_nothing_for_a_user_with_no_guest_yet(self, db_session: Session):
        user = _make_user(db_session, email="noguest@test.com")
        assert get_guest_for_user(db_session, user) is None

    def test_backfills_the_fk_for_a_legacy_guest_matched_only_by_email(self, db_session: Session):
        """A Guest created before this FK existed (or by a path that predates
        crud.guest) has user_account_id=None but a matching email -- must
        still resolve, and get linked going forward."""
        user = _make_user(db_session, email="legacy@test.com")
        legacy_guest = Guest(id="G-LEGACY", name="Legacy Renter", email="legacy@test.com", joined_at=date.today())
        db_session.add(legacy_guest)
        db_session.commit()
        assert legacy_guest.user_account_id is None

        found = get_guest_for_user(db_session, user)
        db_session.commit()

        assert found is not None
        assert found.id == "G-LEGACY"
        db_session.refresh(legacy_guest)
        assert legacy_guest.user_account_id == user.id

    def test_does_not_match_a_guest_already_linked_to_a_different_user(self, db_session: Session):
        owner = _make_user(db_session, email="owner@test.com")
        get_or_create_guest_for_user(db_session, owner)
        db_session.commit()

        other = _make_user(db_session, email="other@test.com")
        assert get_guest_for_user(db_session, other) is None


class TestNotifyUserByGuestUsesTheFk:
    def test_notifies_via_linked_fk_without_an_email_lookup(self, db_session: Session):
        user = _make_user(db_session, email="notifyme@test.com")
        guest = get_or_create_guest_for_user(db_session, user)
        db_session.commit()

        notif_crud_result = notify_user_by_guest(
            db_session, guest,
            title="Test", message="hello", notification_type="test.event",
        )
        db_session.commit()

        assert notif_crud_result is not None
        assert notif_crud_result.recipient_user_id == user.id

    def test_self_heals_an_unlinked_guest_found_by_email(self, db_session: Session):
        user = _make_user(db_session, email="healme@test.com")
        guest = Guest(id="G-HEAL", name="Heal Me", email="healme@test.com", joined_at=date.today())
        db_session.add(guest)
        db_session.commit()
        assert guest.user_account_id is None

        result = notify_user_by_guest(
            db_session, guest,
            title="Test", message="hello", notification_type="test.heal",
        )
        db_session.commit()

        assert result is not None
        assert result.recipient_user_id == user.id
        db_session.refresh(guest)
        assert guest.user_account_id == user.id

    def test_no_op_for_a_guest_with_no_linkable_account(self, db_session: Session):
        guest = Guest(id="G-WALKIN", name="Walk-in Tenant", email="walkin@nowhere.test", joined_at=date.today())
        db_session.add(guest)
        db_session.commit()

        result = notify_user_by_guest(
            db_session, guest,
            title="Test", message="hello", notification_type="test.none",
        )
        assert result is None
        assert db_session.scalar(select(Notification).where(Notification.notification_type == "test.none")) is None
