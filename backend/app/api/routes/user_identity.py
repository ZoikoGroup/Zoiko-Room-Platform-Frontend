from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.correlation import get_correlation_id
from app.crud import identity_verification as crud
from app.crud.audit import log_audit_event
from app.db.session import get_db
from app.models.user_account import UserAccount
from app.schemas.marketplace import IdentityVerificationSubmitRequest, IdentityVerificationUserRead

router = APIRouter(prefix="/api/users/identity-verifications", tags=["user-identity-verifications"])


@router.post("", response_model=IdentityVerificationUserRead, status_code=status.HTTP_201_CREATED)
def submit_identity_verification(
    payload: IdentityVerificationSubmitRequest,
    request: Request,
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """User submits their identity verification document."""
    record = crud.submit_identity_verification_for_user(db, user, payload)
    log_audit_event(db, None, "user_identity_verification.submit", "identity_verification", str(record.id), get_correlation_id(request), reason=f"user:{user.id}")
    db.commit()
    return {
        "id": record.id,
        "document_type": record.document_type,
        "evidence_ref": record.evidence_ref,
        "status": record.status,
        "verified_at": record.verified_at,
        "expires_at": record.expires_at,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "verifier_notes": "",
    }


@router.get("", response_model=list[IdentityVerificationUserRead])
def list_identity_verifications(
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all identity verifications for current user."""
    records = crud.list_user_identity_verifications(db, user)
    return [
        {
            "id": r.id,
            "document_type": r.document_type,
            "evidence_ref": r.evidence_ref,
            "status": r.status,
            "verified_at": r.verified_at,
            "expires_at": r.expires_at,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
            "verifier_notes": "",
        }
        for r in records
    ]


@router.get("/{verification_id}", response_model=IdentityVerificationUserRead)
def get_identity_verification(
    verification_id: int,
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific identity verification."""
    record = crud.get_identity_verification(db, verification_id)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Identity verification not found")
    if record.party_id != user.party_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only view your own identity verifications")
    
    return {
        "id": record.id,
        "document_type": record.document_type,
        "evidence_ref": record.evidence_ref,
        "status": record.status,
        "verified_at": record.verified_at,
        "expires_at": record.expires_at,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "verifier_notes": "",
    }
