"""Regression test: the CHECK constraint on chat_conversations enforces exactly
one of (admin_id, user_id) is non-null.

These tests run against the in-memory SQLite DB, which mirrors the PostgreSQL
CHECK constraint that migration 0018 adds.  They verify the constraint logic
at the application/model level so the bug cannot silently reappear even if
someone forgets to run the migration.
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.chat import ChatConversation
from tests.conftest import _make_admin, _make_user


class TestChatConversationActorConstraint:
    """Verify that exactly one of admin_id / user_id must be set."""

    def test_admin_conversation_is_valid(self, db_session: Session):
        admin = _make_admin(db_session)
        conv = ChatConversation(admin_id=admin.id)
        db_session.add(conv)
        db_session.flush()  # should not raise

    def test_user_conversation_is_valid(self, db_session: Session):
        user = _make_user(db_session)
        conv = ChatConversation(user_id=user.id)
        db_session.add(conv)
        db_session.flush()  # should not raise

    def test_both_set_raises(self, db_session: Session):
        admin = _make_admin(db_session)
        user = _make_user(db_session)
        conv = ChatConversation(admin_id=admin.id, user_id=user.id)
        db_session.add(conv)
        with pytest.raises(Exception):  # IntegrityError or similar
            db_session.flush()

    def test_neither_set_raises(self, db_session: Session):
        conv = ChatConversation()  # type: ignore[call-arg]
        db_session.add(conv)
        with pytest.raises(Exception):
            db_session.flush()


class TestUserChatCreatesConversationCorrectly:
    """Regression: the original bug was user_chat creating a row with
    admin_id=NULL in a NOT-NULL column.  This test verifies the code path."""

    def test_user_route_creates_conversation_with_user_id(
        self, client, db_session: Session
    ):
        user = _make_user(db_session)
        from tests.conftest import auth_user_cookie
        cookies = auth_user_cookie(user)
        r = client.post("/api/users/chat/conversations", cookies=cookies)
        assert r.status_code == 201
        data = r.json()
        assert data["id"] > 0
        # Verify in DB: user_id is set, admin_id is None
        conv = db_session.get(ChatConversation, data["id"])
        assert conv is not None
        assert conv.user_id == user.id
        assert conv.admin_id is None

    def test_admin_route_creates_conversation_with_admin_id(
        self, client, db_session: Session
    ):
        admin = _make_admin(db_session)
        from tests.conftest import auth_admin_cookie
        cookies = auth_admin_cookie(admin)
        r = client.post("/api/admin/chat/conversations", cookies=cookies)
        assert r.status_code == 201
        conv = db_session.get(ChatConversation, r.json()["id"])
        assert conv is not None
        assert conv.admin_id == admin.id
        assert conv.user_id is None
