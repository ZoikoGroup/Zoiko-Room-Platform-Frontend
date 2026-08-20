from datetime import datetime

from app.schemas.common import CamelModel


class MarketReleaseCreate(CamelModel):
    jurisdiction: str
    min_stay_nights: int = 30


class MarketReleaseRead(CamelModel):
    id: int
    jurisdiction: str
    status: str
    min_stay_nights: int
    effective_from: datetime | None
    approved_at: datetime | None
    created_at: datetime


class PropertyCreate(CamelModel):
    address: str
    city: str


class PropertyRead(CamelModel):
    id: int
    owner_party_id: int
    address: str
    city: str
    status: str
    created_at: datetime


class RoomCreate(CamelModel):
    size: int = 0
    has_ensuite: bool = False


class RoomRead(CamelModel):
    id: int
    property_id: int
    room_type: str
    size: int
    has_ensuite: bool
    status: str
    created_at: datetime


class AuthorityRecordCreate(CamelModel):
    room_id: int
    authority_type: str
    evidence_ref: str = ""


class AuthorityRecordRead(CamelModel):
    id: int
    party_id: int
    room_id: int
    authority_type: str
    evidence_ref: str
    verified_at: datetime | None
    expires_at: datetime | None
    status: str
    created_at: datetime


class IdentityVerificationCreate(CamelModel):
    party_id: int | None = None
    document_type: str
    encrypted_reference: str
    evidence_ref: str = ""


class IdentityVerificationRead(CamelModel):
    id: int
    party_id: int
    document_type: str
    encrypted_reference: str
    evidence_ref: str
    verified_at: datetime | None
    expires_at: datetime | None
    verifier_admin_id: int | None
    status: str
    created_at: datetime
    updated_at: datetime


class IdentityVerificationSubmitRequest(CamelModel):
    """User-facing identity verification submission."""

    document_type: str
    encrypted_reference: str
    evidence_ref: str = ""


class IdentityVerificationUserRead(CamelModel):
    """User-facing identity verification response."""

    id: int
    document_type: str
    evidence_ref: str
    status: str
    verified_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime
    verifier_notes: str = ""


class RoomPassportClaimCreate(CamelModel):
    claim_type: str
    value: str
    evidence_tier: str = "self_attested"


class RoomPassportClaimRead(CamelModel):
    id: int
    room_id: int
    claim_type: str
    value: str
    evidence_tier: str
    verified_at: datetime | None
    expires_at: datetime | None
    created_at: datetime


class OccupancyClassificationSet(CamelModel):
    classification: str
    confidence: float = 1.0
    evidence_ref: str = ""
    review_state: str = "APPROVED"


class OccupancyClassificationRead(CamelModel):
    id: int
    room_id: int
    classification: str
    confidence: float
    evidence_ref: str
    jurisdiction: str
    rule_version: int
    review_state: str
    updated_at: datetime
