from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.crud.finance import annotate_payment_context
from app.crud.guest import get_guest_for_user
from app.db.session import get_db
from app.models.finance import SimulatedPayment
from app.models.user_account import UserAccount
from app.schemas.finance import SimulatedPaymentRead

router = APIRouter(prefix="/api/users/payments", tags=["user-payments"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[SimulatedPaymentRead])
def list_user_payment_history(
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Read-only payment history limited to the authenticated user's guest record."""
    guest = get_guest_for_user(db, user)
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
    return [SimulatedPaymentRead.model_validate(annotate_payment_context(p)) for p in payments]
