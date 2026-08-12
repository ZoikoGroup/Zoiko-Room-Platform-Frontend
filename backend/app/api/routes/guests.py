from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_super_admin
from app.crud.guest import list_guests
from app.db.session import get_db
from app.schemas.guest import GuestRead

router = APIRouter(prefix="/api/guests", tags=["guests"], dependencies=[Depends(require_super_admin)])


@router.get("", response_model=list[GuestRead])
def get_guests(db: Session = Depends(get_db)):
    return list_guests(db)
