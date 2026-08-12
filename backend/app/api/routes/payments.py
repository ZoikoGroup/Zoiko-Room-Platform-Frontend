from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_super_admin
from app.crud.payment import list_payments
from app.db.session import get_db
from app.schemas.payment import PaymentRead

router = APIRouter(prefix="/api/payments", tags=["payments"], dependencies=[Depends(require_super_admin)])


@router.get("", response_model=list[PaymentRead])
def get_payments(db: Session = Depends(get_db)):
    return list_payments(db)
