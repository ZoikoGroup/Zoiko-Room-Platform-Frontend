"""Confirms the router-level auth hardening added to the user_* routers
actually rejects unauthenticated requests -- i.e. that no endpoint under
these routers can be reached without a valid zoiko_user_token, independent
of whether the individual route handler also declares the dependency."""

from __future__ import annotations


class TestUnauthenticatedAccessIsRejected:
    def test_user_hosting_requires_auth(self, client):
        r = client.get("/api/users/hosting/properties")
        assert r.status_code == 401

    def test_user_identity_requires_auth(self, client):
        r = client.get("/api/users/identity-verifications")
        assert r.status_code == 401

    def test_user_payments_requires_auth(self, client):
        r = client.get("/api/users/payments")
        assert r.status_code == 401

    def test_user_rentals_requires_auth(self, client):
        r = client.get("/api/users/rentals/applications")
        assert r.status_code == 401

    def test_admin_token_cannot_pass_as_user_auth(self, client, db_session):
        """An admin cookie must not satisfy a USER-only router -- proves the
        two auth planes stay separate rather than one implying the other."""
        from tests.conftest import _make_admin, auth_admin_cookie

        admin = _make_admin(db_session)
        r = client.get("/api/users/rentals/applications", cookies=auth_admin_cookie(admin))
        assert r.status_code == 401
