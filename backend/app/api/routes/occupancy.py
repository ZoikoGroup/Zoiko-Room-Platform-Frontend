from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.correlation import get_correlation_id
from app.crud import finance as finance_crud
from app.crud import leasing as leasing_crud
from app.crud import occupancy as crud
from app.crud.audit import log_audit_event
from app.crud.eligibility import check_move_in_eligibility
from app.crud.events import emit_event
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.finance import ObligationRead
from app.schemas.occupancy import OccupancyRead

router = APIRouter(prefix="/api/occupancy", tags=["occupancy"], dependencies=[Depends(get_current_admin)])


@router.get("/agreements/{agreement_id}/move-in-eligibility")
def get_move_in_eligibility(agreement_id: int, db: Session = Depends(get_db)):
    agreement = leasing_crud.get_agreement_or_404(db, agreement_id)
    reasons = check_move_in_eligibility(db, agreement)
    return {"eligible": not reasons, "reasons": reasons}


@router.post("/agreements/{agreement_id}/confirm-move-in", response_model=OccupancyRead)
def post_confirm_move_in(
    agreement_id: int,
    request: Request,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    agreement = leasing_crud.get_agreement_or_404(db, agreement_id)
    occupancy = crud.confirm_move_in(db, agreement, admin)
    log_audit_event(db, admin, "occupancy.move_in", "occupancy", str(occupancy.id), get_correlation_id(request))
    emit_event(db, "occupancy.active", "occupancy", str(occupancy.id), {"roomId": occupancy.room_id})
    db.commit()
    return crud.to_occupancy_read(occupancy)


@router.get("", response_model=list[OccupancyRead])
def get_occupancies(admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    return [crud.to_occupancy_read(o) for o in crud.list_occupancies_for(db, admin)]


@router.get("/rent-due-check", response_model=list[OccupancyRead])
def get_rent_due_check(admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    return [crud.to_occupancy_read(o) for o in crud.list_occupancies_missing_upcoming_rent(db, admin)]


@router.post("/{occupancy_id}/generate-rent", response_model=ObligationRead | None)
def post_generate_rent(
    occupancy_id: int,
    request: Request,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    occupancy = crud.get_occupancy_or_404(db, occupancy_id)
    obligation = crud.generate_next_rent_obligation(db, occupancy, admin)
    if obligation:
        log_audit_event(db, admin, "occupancy.generate_rent", "occupancy", str(occupancy_id), get_correlation_id(request))
        emit_event(db, "obligation.created", "obligation", str(obligation.id), {"obligationType": "RENT", "occupancyId": occupancy_id})
        db.commit()
        return finance_crud.to_obligation_read(obligation)
    return None


@router.post("/{occupancy_id}/end", response_model=OccupancyRead)
def post_end_occupancy(
    occupancy_id: int,
    request: Request,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    occupancy = crud.get_occupancy_or_404(db, occupancy_id)
    updated = crud.end_occupancy(db, occupancy, admin)
    log_audit_event(db, admin, "occupancy.end", "occupancy", str(occupancy_id), get_correlation_id(request))
    emit_event(db, "occupancy.ended", "occupancy", str(occupancy_id), {})
    db.commit()
    return crud.to_occupancy_read(updated)
