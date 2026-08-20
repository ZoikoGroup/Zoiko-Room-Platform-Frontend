from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.finance import SimulatedPayment
from app.models.guest import Guest
from app.models.user_account import UserAccount
from app.schemas.finance import PaymentAllocationRead, SimulatedPaymentRead

router = APIRouter(prefix="/api/users/payments", tags=["user-payments"])


@router.get("", response_model=list[SimulatedPaymentRead])
def list_user_payment_history(
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Read-only payment history limited to the authenticated user's guest record."""
    guest = db.scalar(select(Guest).where(Guest.email == user.email))
    if not guest:
        return []

    payments = list(
        db.scalars(
            select(SimulatedPayment)
            .options(selectinload(SimulatedPayment.allocations))
            .where(SimulatedPayment.guest_id == guest.id)
            .order_by(SimulatedPayment.created_at.desc())
        )
    )
    return [
        SimulatedPaymentRead(
            id=payment.id,
            guest_id=payment.guest_id,
            amount=payment.amount,
            currency=payment.currency,
            idempotency_key=payment.idempotency_key,
            status=payment.status,
            created_at=payment.created_at,
            confirmed_at=payment.confirmed_at,
            allocations=[
                PaymentAllocationRead(
                    id=allocation.id,
                    payment_id=allocation.payment_id,
                    obligation_id=allocation.obligation_id,
                    amount_allocated=allocation.amount_allocated,
                    created_at=allocation.created_at,
                )
                for allocation in payment.allocations
            ],
        )
        for payment in payments
    ]
