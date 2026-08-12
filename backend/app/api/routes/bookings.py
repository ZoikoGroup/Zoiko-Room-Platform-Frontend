from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_super_admin
from app.crud.booking import create_booking, list_bookings
from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingRead

router = APIRouter(prefix="/api/bookings", tags=["bookings"], dependencies=[Depends(require_super_admin)])


@router.get("", response_model=list[BookingRead])
def get_bookings(db: Session = Depends(get_db)):
    return list_bookings(db)


@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def post_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    return create_booking(db, payload)
