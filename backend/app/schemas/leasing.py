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
