from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.crud.property import get_room
from app.crud.room_passport import add_claim, list_claims_for_room
from app.db.session import get_db
from app.schemas.marketplace import RoomPassportClaimCreate, RoomPassportClaimRead

router = APIRouter(prefix="/api/rooms", tags=["room-passport"], dependencies=[Depends(get_current_admin)])


def _get_room_or_404(db: Session, room_id: int):
    room = get_room(db, room_id)
    if not room:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    return room


@router.get("/{room_id}/passport/claims", response_model=list[RoomPassportClaimRead])
def get_claims(room_id: int, db: Session = Depends(get_db)):
    _get_room_or_404(db, room_id)
    return list_claims_for_room(db, room_id)


@router.post("/{room_id}/passport/claims", response_model=RoomPassportClaimRead, status_code=status.HTTP_201_CREATED)
def post_claim(room_id: int, payload: RoomPassportClaimCreate, db: Session = Depends(get_db)):
    room = _get_room_or_404(db, room_id)
    return add_claim(db, room, payload)
