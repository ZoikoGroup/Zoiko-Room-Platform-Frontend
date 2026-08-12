from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.room import Room
from app.models.room_passport import RoomPassportClaim
from app.schemas.marketplace import RoomPassportClaimCreate


def list_claims_for_room(db: Session, room_id: int) -> list[RoomPassportClaim]:
    return list(db.scalars(select(RoomPassportClaim).where(RoomPassportClaim.room_id == room_id).order_by(RoomPassportClaim.id)))


def add_claim(db: Session, room: Room, data: RoomPassportClaimCreate) -> RoomPassportClaim:
    claim = RoomPassportClaim(
        room_id=room.id,
        claim_type=data.claim_type,
        value=data.value,
        evidence_tier=data.evidence_tier,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim
