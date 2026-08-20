from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.party import get_or_create_default_party
from app.models.admin_user import AdminUser
from app.models.identity_verification import IdentityVerification, DOCUMENT_TYPES, IDENTITY_STATUSES
from app.models.party import Party
from app.models.user_account import UserAccount
from app.schemas.marketplace import IdentityVerificationCreate

IDENTITY_VERIFICATION_VALIDITY_DAYS = 365


def list_identity_verifications(db: Session, admin: AdminUser, party_id: int | None = None) -> list[IdentityVerification]:
    query = select(IdentityVerification).order_by(IdentityVerification.id)
    if admin.role != "super_admin":
        party = get_or_create_default_party(db, admin)
        query = query.where(IdentityVerification.party_id == party.id)
    elif party_id is not None:
        query = query.where(IdentityVerification.party_id == party_id)
    return list(db.scalars(query))


def get_identity_verification(db: Session, verification_id: int) -> IdentityVerification | None:
    return db.get(IdentityVerification, verification_id)


def submit_identity_verification(db: Session, admin: AdminUser, data: IdentityVerificationCreate) -> IdentityVerification:
    if data.document_type not in DOCUMENT_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid document type")
    if not data.encrypted_reference:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Encrypted reference is required")

    if data.party_id is not None:
        if admin.role != "super_admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only super admins may create verification records for another party")
        party = db.get(Party, data.party_id)
        if not party:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Party not found")
    else:
        party = get_or_create_default_party(db, admin)

    record = IdentityVerification(
        party_id=party.id,
        document_type=data.document_type,
        encrypted_reference=data.encrypted_reference,
        evidence_ref=data.evidence_ref,
        status="pending",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def verify_identity_verification(db: Session, record: IdentityVerification, verifier: AdminUser) -> IdentityVerification:
    if verifier.role != "super_admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Super admin access required")
    now = datetime.now(timezone.utc)
    record.status = "verified"
    record.verified_at = now
    record.expires_at = now + timedelta(days=IDENTITY_VERIFICATION_VALIDITY_DAYS)
    record.verifier_admin_id = verifier.id
    record.updated_at = now
    db.commit()
    db.refresh(record)
    return record


def reject_identity_verification(db: Session, record: IdentityVerification, verifier: AdminUser) -> IdentityVerification:
    if verifier.role != "super_admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Super admin access required")
    now = datetime.now(timezone.utc)
    record.status = "rejected"
    record.verifier_admin_id = verifier.id
    record.updated_at = now
    db.commit()
    db.refresh(record)
    return record


def get_verified_identity_for_party(db: Session, party_id: int) -> IdentityVerification | None:
    now = datetime.now(timezone.utc)
    return db.scalar(
        select(IdentityVerification)
        .where(
            IdentityVerification.party_id == party_id,
            IdentityVerification.status == "verified",
            (IdentityVerification.expires_at.is_(None)) | (IdentityVerification.expires_at > now),
        )
        .order_by(IdentityVerification.id.desc())
    )


def submit_identity_verification_for_user(db: Session, user_account: "UserAccount", data: IdentityVerificationCreate) -> IdentityVerification:
    """User submits their own identity verification for PENDING approval."""
    if data.document_type not in DOCUMENT_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid document type")
    if not data.encrypted_reference:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Encrypted reference is required")
    if not user_account.party_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "User has no associated party")

    record = IdentityVerification(
        party_id=user_account.party_id,
        document_type=data.document_type,
        encrypted_reference=data.encrypted_reference,
        evidence_ref=data.evidence_ref,
        status="pending",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_user_identity_verifications(db: Session, user_account: "UserAccount") -> list[IdentityVerification]:
    """List all identity verifications for a user's party."""
    if not user_account.party_id:
        return []
    return list(
        db.scalars(
            select(IdentityVerification)
            .where(IdentityVerification.party_id == user_account.party_id)
            .order_by(IdentityVerification.id.desc())
        )
    )


def request_additional_evidence(db: Session, record: IdentityVerification, verifier: AdminUser, note: str = "") -> IdentityVerification:
    """Super admin requests additional evidence from user."""
    if verifier.role != "super_admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Super admin access required")
    now = datetime.now(timezone.utc)
    record.status = "additional_evidence_required"
    record.verifier_admin_id = verifier.id
    record.updated_at = now
    db.commit()
    db.refresh(record)
    return record

