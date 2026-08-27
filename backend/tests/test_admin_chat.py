"""Integration tests for the admin chatbot endpoints (/api/admin/chat/*)."""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

from sqlalchemy.orm import Session

from app.models.chat import ChatConversation, ChatMessage
from tests.conftest import (
    _make_admin,
    auth_admin_cookie,
)

PREFIX = "/api/admin/chat"


# ── Helpers ──────────────────────────────────────────────────────────────


def _create_conversation(client, cookies):
    r = client.post(f"{PREFIX}/conversations", cookies=cookies)
    assert r.status_code == 201, r.text
    return r.json()


# ── Conversation CRUD ────────────────────────────────────────────────────


class TestConversationCRUD:
    def test_create_conversation(self, client, db_session: Session):
        admin = _make_admin(db_session)
        cookies = auth_admin_cookie(admin)
        conv = _create_conversation(client, cookies)
        assert conv["id"] > 0
        assert conv["title"] == "New conversation"

    def test_list_conversations(self, client, db_session: Session):
        admin = _make_admin(db_session)
        cookies = auth_admin_cookie(admin)
        _create_conversation(client, cookies)
        _create_conversation(client, cookies)
        r = client.get(f"{PREFIX}/conversations", cookies=cookies)
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_list_only_own_conversations(self, client, db_session: Session):
        admin_a = _make_admin(db_session, email="a@test.com")
        admin_b = _make_admin(db_session, email="b@test.com")
        cookies_a = auth_admin_cookie(admin_a)
        cookies_b = auth_admin_cookie(admin_b)
        _create_conversation(client, cookies_a)
        _create_conversation(client, cookies_a)
        _create_conversation(client, cookies_b)
        r = client.get(f"{PREFIX}/conversations", cookies=cookies_a)
        assert r.status_code == 200
        assert len(r.json()) == 2
        r = client.get(f"{PREFIX}/conversations", cookies=cookies_b)
        assert len(r.json()) == 1

    def test_delete_conversation(self, client, db_session: Session):
        admin = _make_admin(db_session)
        cookies = auth_admin_cookie(admin)
        conv = _create_conversation(client, cookies)
        r = client.delete(f"{PREFIX}/conversations/{conv['id']}", cookies=cookies)
        assert r.status_code == 204
        r = client.get(f"{PREFIX}/conversations", cookies=cookies)
        assert len(r.json()) == 0

    def test_delete_other_admins_conversation_returns_404(self, client, db_session: Session):
        admin_a = _make_admin(db_session, email="a@test.com")
        admin_b = _make_admin(db_session, email="b@test.com")
        conv = _create_conversation(client, auth_admin_cookie(admin_a))
        r = client.delete(f"{PREFIX}/conversations/{conv['id']}", cookies=auth_admin_cookie(admin_b))
        assert r.status_code == 404

    def test_list_messages_empty(self, client, db_session: Session):
        admin = _make_admin(db_session)
        cookies = auth_admin_cookie(admin)
        conv = _create_conversation(client, cookies)
        r = client.get(f"{PREFIX}/conversations/{conv['id']}/messages", cookies=cookies)
        assert r.status_code == 200
        assert r.json() == []

    def test_get_other_admins_messages_returns_404(self, client, db_session: Session):
        admin_a = _make_admin(db_session, email="a@test.com")
        admin_b = _make_admin(db_session, email="b@test.com")
        conv = _create_conversation(client, auth_admin_cookie(admin_a))
        r = client.get(f"{PREFIX}/conversations/{conv['id']}/messages", cookies=auth_admin_cookie(admin_b))
        assert r.status_code == 404


# ── Auth ──────────────────────────────────────────────────────────────────


class TestAuth:
    def test_unauthenticated_returns_401(self, client):
        r = client.get(f"{PREFIX}/conversations")
        assert r.status_code == 401

    def test_invalid_token_returns_401(self, client):
        r = client.get(f"{PREFIX}/conversations", cookies={"zoiko_admin_token": "bad"})
        assert r.status_code == 401

    def test_inactive_admin_returns_401(self, client, db_session: Session):
        admin = _make_admin(db_session)
        admin.is_active = False
        db_session.flush()
        r = client.get(f"{PREFIX}/conversations", cookies=auth_admin_cookie(admin))
        assert r.status_code == 401

    def test_pending_admin_returns_401(self, client, db_session: Session):
        admin = _make_admin(db_session)
        admin.approval_status = "pending"
        db_session.flush()
        r = client.get(f"{PREFIX}/conversations", cookies=auth_admin_cookie(admin))
        assert r.status_code == 401


# ── Message streaming (mocked Groq) ──────────────────────────────────────


class TestMessageStream:
    def _mock_stream(self, text="Hello from assistant"):
        """Return a mock ``stream_assistant_reply`` that yields a text event + done."""
        def _stream(db, actor, history):
            yield "text", {"text": text}
            yield "done", {"blocks": [{"type": "text", "text": text}]}
        return _stream

    def test_send_message_creates_user_and_assistant_messages(
        self, client, db_session: Session
    ):
        admin = _make_admin(db_session)
        cookies = auth_admin_cookie(admin)
        conv = _create_conversation(client, cookies)

        with patch("app.api.routes.chatbot.stream_assistant_reply", self._mock_stream()):
            r = client.post(
                f"{PREFIX}/conversations/{conv['id']}/messages/stream",
                json={"content": "Show my bookings"},
                cookies=cookies,
            )
            assert r.status_code == 200
            assert "text/event-stream" in r.headers["content-type"]

            # Parse SSE events
            events = self._parse_sse(r.text)
            types = [e["event"] for e in events]
            assert "text" in types
            assert "done" in types

    def test_empty_message_returns_422(self, client, db_session: Session):
        admin = _make_admin(db_session)
        cookies = auth_admin_cookie(admin)
        conv = _create_conversation(client, cookies)
        r = client.post(
            f"{PREFIX}/conversations/{conv['id']}/messages/stream",
            json={"content": "   "},
            cookies=cookies,
        )
        assert r.status_code == 422

    def test_conversation_title_auto_set_from_first_message(
        self, client, db_session: Session
    ):
        admin = _make_admin(db_session)
        cookies = auth_admin_cookie(admin)
        conv = _create_conversation(client, cookies)

        with patch("app.api.routes.chatbot.stream_assistant_reply", self._mock_stream()):
            client.post(
                f"{PREFIX}/conversations/{conv['id']}/messages/stream",
                json={"content": "Revenue trend please"},
                cookies=cookies,
            )
        r = client.get(f"{PREFIX}/conversations", cookies=cookies)
        updated = next(c for c in r.json() if c["id"] == conv["id"])
        assert updated["title"] == "Revenue trend please"

    def test_rate_limit_error_emits_error_event(self, client, db_session: Session):
        from groq import RateLimitError

        admin = _make_admin(db_session)
        cookies = auth_admin_cookie(admin)
        conv = _create_conversation(client, cookies)

        def _raise_rate_limit(db, actor, history):
            raise RateLimitError(
                message="rate limited",
                response=MagicMock(status_code=429, headers={}),
                body=None,
            )

        with patch("app.api.routes.chatbot.stream_assistant_reply", _raise_rate_limit):
            r = client.post(
                f"{PREFIX}/conversations/{conv['id']}/messages/stream",
                json={"content": "test"},
                cookies=cookies,
            )
            assert r.status_code == 200
            events = self._parse_sse(r.text)
            error_events = [e for e in events if e["event"] == "error"]
            assert len(error_events) == 1
            assert "busy" in error_events[0]["data"]["message"].lower()

    @staticmethod
    def _parse_sse(text: str) -> list[dict]:
        events = []
        for block in text.strip().split("\n\n"):
            event_type = ""
            data_lines = []
            for line in block.split("\n"):
                if line.startswith("event: "):
                    event_type = line[7:]
                elif line.startswith("data: "):
                    data_lines.append(line[6:])
            if event_type:
                data = json.loads("".join(data_lines))
                events.append({"event": event_type, "data": data})
        return events


# ── Super-admin-only tool gating ─────────────────────────────────────────


class TestToolGating:
    def test_super_admin_has_all_tools(self, client, db_session: Session):
        from app.services.chat_service import groq_tool_definitions

        admin = _make_admin(db_session, role="super_admin")
        defs = groq_tool_definitions(admin)
        names = {d["function"]["name"] for d in defs}
        assert "list_bookings" in names
        assert "list_guests" in names
        assert "list_reviews" in names
        assert "list_payments" in names
        assert "revenue_trend" in names

    def test_admin_missing_super_admin_tools(self, client, db_session: Session):
        from app.services.chat_service import groq_tool_definitions

        admin = _make_admin(db_session, role="admin")
        defs = groq_tool_definitions(admin)
        names = {d["function"]["name"] for d in defs}
        assert "list_bookings" not in names
        assert "list_guests" not in names
        assert "list_reviews" not in names
        assert "revenue_trend" not in names

    def test_user_tools_not_in_admin_toolset(self, client, db_session: Session):
        from app.services.chat_service import groq_tool_definitions

        admin = _make_admin(db_session)
        defs = groq_tool_definitions(admin)
        names = {d["function"]["name"] for d in defs}
        assert "search_listings" not in names
        assert "my_applications" not in names
        assert "my_occupancies" not in names
