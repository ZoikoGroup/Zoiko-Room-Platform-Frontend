from datetime import date, datetime

from app.schemas.booking import NewGuestInput
from app.schemas.common import CamelModel


class ApplicationCreate(CamelModel):
    listing_id: str
    guest_id: str | None = None
    new_guest: NewGuestInput | None = None
    message: str = ""
    desired_move_in: date | None = None


class ApplicationDecisionRead(CamelModel):
    id: int
    decision: str
    reason_code: str
    note: str
    decided_by_admin_id: int
    decided_at: datetime


class ApplicationDecide(CamelModel):
    decision: str
    reason_code: str = ""
    note: str = ""


class ApplicationUpdate(CamelModel):
    message: str | None = None
    desired_move_in: date | None = None


class OfferTermsCreate(CamelModel):
    monthly_rent: float
    deposit_amount: float
    start_date: date
    term_months: int


class OfferTermsRead(CamelModel):
    id: int
    version: int
    monthly_rent: float
    deposit_amount: float
    start_date: date
    term_months: int
    created_at: datetime


class AgreementRead(CamelModel):
    id: int
    offer_id: int
    version: int
    status: str
    content_ref: str
    signed_by_provider_at: datetime | None
    signed_by_renter_at: datetime | None
    signature_ref: str
    created_at: datetime


class AgreementSign(CamelModel):
    as_party: str  # "provider" | "renter"


class OfferRead(CamelModel):
    id: int
    application_id: int
    listing_id: str
    guest_id: str
    status: str
    current_version: int
    created_at: datetime
    terms: list[OfferTermsRead] = []
    agreement: AgreementRead | None = None


class ApplicationRead(CamelModel):
    id: int
    listing_id: str
    guest_id: str
    guest_name: str
    guest_email: str
    status: str
    message: str
    desired_move_in: date | None
    submitted_at: datetime
    updated_at: datetime
    decisions: list[ApplicationDecisionRead] = []
    offer: OfferRead | None = None


class UserApplicationSubmitRequest(CamelModel):
    """User submitting a rental application."""

    listing_id: str
    message: str = ""
    desired_move_in: date | None = None


class UserApplicationRead(CamelModel):
    """User-facing application view."""

    id: int
    listing_id: str
    status: str
    message: str
    desired_move_in: date | None
    submitted_at: datetime
    updated_at: datetime


class UserOccupancyRead(CamelModel):
    """User-facing occupancy/rental view."""

    id: int
    listing_id: str
    room_id: int
    status: str
    move_in_date: date | None
    expected_end_date: date | None
    move_out_date: date | None
    created_at: datetime
    ended_at: datetime | None


class SubletRequestCreate(CamelModel):
    """User submitting a sublet request."""

    occupancy_id: int
    proposed_renter_party_id: int
    authority_evidence_ref: str = ""


class SubletRequestRead(CamelModel):
    """Read view for sublet request."""

    id: int
    current_occupancy_id: int
    proposed_renter_party_id: int
    status: str
    authority_evidence_ref: str
    admin_decision: str
    admin_notes: str
    decided_by_admin_id: int | None
    created_at: datetime
    decided_at: datetime | None


class SubletRequestDecision(CamelModel):
    """Optional review notes recorded with a sublet approval or rejection."""

    notes: str = ""
