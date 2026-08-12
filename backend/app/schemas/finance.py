from datetime import date, datetime

from app.schemas.common import CamelModel


class ObligationRead(CamelModel):
    id: int
    obligation_type: str
    money_plane: str
    amount: float
    currency: str
    due_date: date
    status: str
    guest_id: str
    agreement_id: int | None
    occupancy_id: int | None
    payout_id: int | None
    created_at: datetime


class PaymentAllocationInput(CamelModel):
    obligation_id: int
    amount: float


class SimulatedPaymentCreate(CamelModel):
    guest_id: str
    amount: float
    currency: str = "INR"
    idempotency_key: str


class PaymentConfirm(CamelModel):
    allocations: list[PaymentAllocationInput]


class PaymentAllocationRead(CamelModel):
    id: int
    payment_id: int
    obligation_id: int
    amount_allocated: float
    created_at: datetime


class SimulatedPaymentRead(CamelModel):
    id: int
    guest_id: str
    amount: float
    currency: str
    idempotency_key: str
    status: str
    created_at: datetime
    confirmed_at: datetime | None
    allocations: list[PaymentAllocationRead] = []


class DepositRecordRead(CamelModel):
    id: int
    obligation_id: int
    status: str
    held_amount: float
    released_amount: float
    released_at: datetime | None
    notes: str


class DepositRelease(CamelModel):
    amount: float
    notes: str = ""


class PayoutRunRequest(CamelModel):
    party_id: int
    period_key: str


class PayoutRecordRead(CamelModel):
    id: int
    party_id: int
    period_key: str
    amount: float
    currency: str
    status: str
    hold_reason: str
    created_at: datetime
    paid_at: datetime | None


class RefundRequestCreate(CamelModel):
    payment_id: int
    obligation_id: int
    amount: float
    reason: str = ""


class RefundDecide(CamelModel):
    approve: bool


class RefundRequestRead(CamelModel):
    id: int
    payment_id: int
    obligation_id: int
    amount: float
    reason: str
    status: str
    requested_by_admin_id: int
    decided_by_admin_id: int | None
    created_at: datetime
    decided_at: datetime | None


class DisputeCreate(CamelModel):
    payment_id: int | None = None
    occupancy_id: int | None = None
    category: str
    description: str = ""


class DisputeResolve(CamelModel):
    status: str  # "RESOLVED" | "REJECTED"
    resolution_notes: str = ""


class DisputeRead(CamelModel):
    id: int
    payment_id: int | None
    occupancy_id: int | None
    category: str
    description: str
    status: str
    opened_at: datetime
    resolved_at: datetime | None
    resolution_notes: str


class ReconciliationRunRead(CamelModel):
    id: int
    run_at: datetime
    totals: dict
    mismatches: list
    status: str
