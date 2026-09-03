"""Authorization tests for the secure identity-document view/download flow
(#7 in the Anil task list) -- this was audited as already correct by reading
the code, but had zero automated coverage proving it. Redirects
settings.identity_upload_dir to a pytest tmp_path so no real repo directories
are touched and cleanup is automatic.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.identity_verification import IdentityVerification
from app.models.party import Party
from tests.conftest import _make_admin, _make_user, auth_admin_cookie, auth_user_cookie


def _make_verification_with_document(db: Session, tmp_path, *, party_id: int) -> IdentityVerification:
    stored_filename = "test-doc.pdf"
    (tmp_path / stored_filename).write_bytes(b"%PDF-1.4 fake content")

    record = IdentityVerification(
        party_id=party_id,
        document_type="passport",
        document_file_path=stored_filename,
        document_file_original_name="passport.pdf",
        document_file_content_type="application/pdf",
        document_file_size=21,
        status="pending",
    )
    db.add(record)
    db.commit()
    return record


class TestUserDocumentAccess:
    def test_owner_can_download_own_document(self, client, db_session: Session, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "identity_upload_dir", str(tmp_path))
        party = Party(party_type="renter", status="active", jurisdiction="IN")
        db_session.add(party)
        db_session.flush()
        user = _make_user(db_session, email="owner@test.com")
        user.party_id = party.id
        db_session.commit()
        record = _make_verification_with_document(db_session, tmp_path, party_id=party.id)

        r = client.get(f"/api/users/identity-verifications/{record.id}/document", cookies=auth_user_cookie(user))
        assert r.status_code == 200, r.text
        assert r.content == b"%PDF-1.4 fake content"

    def test_other_user_cannot_download_someone_elses_document(self, client, db_session: Session, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "identity_upload_dir", str(tmp_path))
        owner_party = Party(party_type="renter", status="active", jurisdiction="IN")
        other_party = Party(party_type="renter", status="active", jurisdiction="IN")
        db_session.add_all([owner_party, other_party])
        db_session.flush()
        owner = _make_user(db_session, email="doc-owner@test.com")
        owner.party_id = owner_party.id
        other = _make_user(db_session, email="stranger@test.com")
        other.party_id = other_party.id
        db_session.commit()
        record = _make_verification_with_document(db_session, tmp_path, party_id=owner_party.id)

        r = client.get(f"/api/users/identity-verifications/{record.id}/document", cookies=auth_user_cookie(other))
        assert r.status_code == 403, r.text

    def test_unauthenticated_request_is_rejected(self, client, db_session: Session, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "identity_upload_dir", str(tmp_path))
        party = Party(party_type="renter", status="active", jurisdiction="IN")
        db_session.add(party)
        db_session.flush()
        record = _make_verification_with_document(db_session, tmp_path, party_id=party.id)

        r = client.get(f"/api/users/identity-verifications/{record.id}/document")
        assert r.status_code == 401, r.text

    def test_missing_file_on_disk_returns_404_even_with_db_row(self, client, db_session: Session, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "identity_upload_dir", str(tmp_path))
        party = Party(party_type="renter", status="active", jurisdiction="IN")
        db_session.add(party)
        db_session.flush()
        user = _make_user(db_session, email="ghost-file@test.com")
        user.party_id = party.id
        db_session.commit()

        record = IdentityVerification(
            party_id=party.id,
            document_type="passport",
            document_file_path="never-actually-written.pdf",
            status="pending",
        )
        db_session.add(record)
        db_session.commit()

        r = client.get(f"/api/users/identity-verifications/{record.id}/document", cookies=auth_user_cookie(user))
        assert r.status_code == 404, r.text


class TestAdminDocumentAccess:
    def test_super_admin_can_download_any_users_document(self, client, db_session: Session, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "identity_upload_dir", str(tmp_path))
        party = Party(party_type="renter", status="active", jurisdiction="IN")
        db_session.add(party)
        db_session.flush()
        record = _make_verification_with_document(db_session, tmp_path, party_id=party.id)
        admin = _make_admin(db_session, email="doc-admin@test.com", role="super_admin")

        r = client.get(f"/api/identity-verifications/{record.id}/document", cookies=auth_admin_cookie(admin))
        assert r.status_code == 200, r.text
        assert r.content == b"%PDF-1.4 fake content"

    def test_plain_admin_cannot_download_document(self, client, db_session: Session, tmp_path, monkeypatch):
        """Only super_admin is gated in for the admin-side document route --
        see require_super_admin on identity_verification.py's download route."""
        monkeypatch.setattr(settings, "identity_upload_dir", str(tmp_path))
        party = Party(party_type="renter", status="active", jurisdiction="IN")
        db_session.add(party)
        db_session.flush()
        record = _make_verification_with_document(db_session, tmp_path, party_id=party.id)
        admin = _make_admin(db_session, email="plain-admin@test.com", role="admin")

        r = client.get(f"/api/identity-verifications/{record.id}/document", cookies=auth_admin_cookie(admin))
        assert r.status_code == 403, r.text

    def test_unauthenticated_admin_route_is_rejected(self, client, db_session: Session, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "identity_upload_dir", str(tmp_path))
        party = Party(party_type="renter", status="active", jurisdiction="IN")
        db_session.add(party)
        db_session.flush()
        record = _make_verification_with_document(db_session, tmp_path, party_id=party.id)

        r = client.get(f"/api/identity-verifications/{record.id}/document")
        assert r.status_code == 401, r.text
