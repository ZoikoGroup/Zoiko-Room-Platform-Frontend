from datetime import date as date_
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.correlation import get_correlation_id
from app.crud import leasing as leasing_crud
from app.crud import occupancy as occupancy_crud
from app.crud import sublet as sublet_crud
from app.crud.audit import log_audit_event
from app.crud.events import emit_event
from app.crud.eligibility import check_offer_eligibility
from app.crud.identity_verification import get_verified_identity_for_party
from app.crud.ids import dicebear_avatar, new_id
from app.crud import notification as notif_crud
from app.db.session import get_db
from app.models.guest import Guest
from app.models.leasing import Application
from app.models.listing import Listing
from app.models.occupancy import Occupancy
from app.models.user_account import UserAccount
from app.schemas.leasing import UserApplicationRead, UserApplicationSubmitRequest, UserOccupancyRead, SubletRequestCreate, SubletRequestRead

router = APIRouter(prefix="/api/users/rentals", tags=["user-rentals"])


def _get_or_create_user_guest(db: Session, user: UserAccount) -> Guest:
    """Get or create a Guest entry linked to a user."""
    existing = db.scalar(select(Guest).where(Guest.email == user.email))
    if existing:
        return existing

    guest = Guest(
        id=new_id("G"),
        name=user.full_name,
        email=user.email,
        phone=user.phone,
        avatar=dicebear_avatar(user.full_name),
        location="",
        joined_at=date_.today(),
        status="active",
    )
    db.add(guest)
    db.flush()
    return guest


@router.post("/applications", response_model=UserApplicationRead, status_code=status.HTTP_201_CREATED)
def submit_rental_application(
    payload: UserApplicationSubmitRequest,
    request: Request,
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """User submits a rental application for a listing.
    Requires verified identity before application can proceed.
    """
    # Check identity verification
    if not user.party_id or not get_verified_identity_for_party(db, user.party_id):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You must complete identity verification before submitting applications",
        )

    # Get or create guest for this user
    guest = _get_or_create_user_guest(db, user)

    # Submit application using existing CRUD logic
    from app.schemas.leasing import ApplicationCreate

    app_data = ApplicationCreate(listing_id=payload.listing_id, guest_id=guest.id, message=payload.message, desired_move_in=payload.desired_move_in)

    try:
        application = leasing_crud.submit_application(db, app_data)
        log_audit_event(db, None, "user_application.submit", "application", str(application.id), get_correlation_id(request), reason=f"user:{user.id}")

        listing = db.get(Listing, application.listing_id)
        if listing and listing.party_id:
            notif_crud.notify_user_by_party(
                db, listing.party_id,
                title="New rental application",
                message=f"{user.full_name} applied for your listing \"{listing.name}\".",
                notification_type="application.received",
                related_entity_type="application", related_entity_id=str(application.id),
            )
        notif_crud.notify_all_super_admins(
            db,
            title="New rental application submitted",
            message=f"{user.full_name} applied for listing {application.listing_id}.",
            notification_type="application.submitted",
            related_entity_type="application", related_entity_id=str(application.id),
        )

        db.commit()

        return UserApplicationRead(
            id=application.id,
            listing_id=application.listing_id,
            status=application.status,
            message=application.message,
            desired_move_in=application.desired_move_in,
            submitted_at=application.submitted_at,
            updated_at=application.updated_at,
        )
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.get("/applications", response_model=list[UserApplicationRead])
def list_user_applications(
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all rental applications submitted by current user."""
    if not user.party_id:
        return []

    # Get guest associated with this user
    guest = db.scalar(select(Guest).where(Guest.email == user.email))
    if not guest:
        return []

    applications = list(
        db.scalars(
            select(Application)
            .where(Application.guest_id == guest.id)
            .order_by(Application.submitted_at.desc())
        )
    )

    return [
        UserApplicationRead(
            id=app.id,
            listing_id=app.listing_id,
            status=app.status,
            message=app.message,
            desired_move_in=app.desired_move_in,
            submitted_at=app.submitted_at,
            updated_at=app.updated_at,
        )
        for app in applications
    ]


@router.get("/applications/{application_id}", response_model=UserApplicationRead)
def get_application_details(
    application_id: int,
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific application."""
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")

    # Verify the application belongs to this user
    guest = db.scalar(select(Guest).where(Guest.email == user.email))
    if not guest or application.guest_id != guest.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only view your own applications")

    return UserApplicationRead(
        id=application.id,
        listing_id=application.listing_id,
        status=application.status,
        message=application.message,
        desired_move_in=application.desired_move_in,
        submitted_at=application.submitted_at,
        updated_at=application.updated_at,
    )


@router.post("/applications/{application_id}/withdraw", response_model=UserApplicationRead)
def withdraw_application(
    application_id: int,
    request: Request,
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """User withdraws a rental application."""
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")

    # Verify ownership
    guest = db.scalar(select(Guest).where(Guest.email == user.email))
    if not guest or application.guest_id != guest.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only withdraw your own applications")

    if application.status != "SUBMITTED":
        raise HTTPException(status.HTTP_409_CONFLICT, "Can only withdraw applications in SUBMITTED status")

    application.status = "WITHDRAWN"
    application.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(application)

    log_audit_event(
        db,
        None,
        "user_application.withdraw",
        "application",
        str(application_id),
        get_correlation_id(request),
        reason=f"user:{user.id}",
    )
    db.commit()

    return UserApplicationRead(
        id=application.id,
        listing_id=application.listing_id,
        status=application.status,
        message=application.message,
        desired_move_in=application.desired_move_in,
        submitted_at=application.submitted_at,
        updated_at=application.updated_at,
    )


@router.get("/occupancies", response_model=list[UserOccupancyRead])
def list_user_occupancies(
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all active and past occupancies (rentals) for current user."""
    guest = db.scalar(select(Guest).where(Guest.email == user.email))
    if not guest:
        return []

    occupancies = list(
        db.scalars(
            select(Occupancy)
            .where(Occupancy.guest_id == guest.id)
            .order_by(Occupancy.created_at.desc())
        )
    )

    return [
        UserOccupancyRead(
            id=occ.id,
            listing_id=occ.listing_id,
            room_id=occ.room_id,
            status=occ.status,
            move_in_date=occ.move_in_date,
            expected_end_date=occ.expected_end_date,
            move_out_date=occ.move_out_date,
            created_at=occ.created_at,
            ended_at=occ.ended_at,
        )
        for occ in occupancies
    ]


@router.get("/occupancies/{occupancy_id}", response_model=UserOccupancyRead)
def get_occupancy_details(
    occupancy_id: int,
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific occupancy/rental."""
    occupancy = db.get(Occupancy, occupancy_id)
    if not occupancy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Occupancy not found")

    # Verify ownership
    guest = db.scalar(select(Guest).where(Guest.email == user.email))
    if not guest or occupancy.guest_id != guest.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only view your own occupancies")

    return UserOccupancyRead(
        id=occupancy.id,
        listing_id=occupancy.listing_id,
        room_id=occupancy.room_id,
        status=occupancy.status,
        move_in_date=occupancy.move_in_date,
        expected_end_date=occupancy.expected_end_date,
        move_out_date=occupancy.move_out_date,
        created_at=occupancy.created_at,
        ended_at=occupancy.ended_at,
    )


@router.post("/occupancies/{occupancy_id}/sublet-request", response_model=SubletRequestRead, status_code=status.HTTP_201_CREATED)
def submit_sublet_request(
    occupancy_id: int,
    payload: SubletRequestCreate,
    request: Request,
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Current renter requests to sublet their occupancy."""
    occupancy = db.get(Occupancy, occupancy_id)
    if not occupancy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Occupancy not found")
    if payload.occupancy_id != occupancy_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "occupancyId must match the requested occupancy")

    # Verify the user owns the occupancy
    guest = db.scalar(select(Guest).where(Guest.email == user.email))
    if not guest or occupancy.guest_id != guest.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only sublet your own occupancies")

    # Verify proposed renter has identity verification
    if not sublet_crud.verify_sublet_identity(db, type("SubletRequest", (), {"proposed_renter_party_id": payload.proposed_renter_party_id})()):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Proposed renter must have verified identity")

    sublet_request = sublet_crud.submit_sublet_request(
        db, user, occupancy_id, payload.proposed_renter_party_id, payload.authority_evidence_ref
    )

    log_audit_event(db, None, "user_sublet_request.submit", "sublet_request", str(sublet_request.id), get_correlation_id(request), reason=f"user:{user.id}")
    emit_event(db, "sublet_request.submitted", "sublet_request", str(sublet_request.id), {"occupancyId": occupancy_id})
    db.commit()

    return SubletRequestRead(
        id=sublet_request.id,
        current_occupancy_id=sublet_request.current_occupancy_id,
        proposed_renter_party_id=sublet_request.proposed_renter_party_id,
        status=sublet_request.status,
        authority_evidence_ref=sublet_request.authority_evidence_ref,
        admin_decision=sublet_request.admin_decision,
        admin_notes=sublet_request.admin_notes,
        decided_by_admin_id=sublet_request.decided_by_admin_id,
        created_at=sublet_request.created_at,
        decided_at=sublet_request.decided_at,
    )


@router.get("/sublet-requests", response_model=list[SubletRequestRead])
def list_user_sublet_requests(
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all sublet requests initiated by current user."""
    from app.models.sublet_request import SubletRequest

    guest = db.scalar(select(Guest).where(Guest.email == user.email))
    if not guest:
        return []

    sublet_requests = list(
        db.scalars(
            select(SubletRequest)
            .join(Occupancy, Occupancy.id == SubletRequest.current_occupancy_id)
            .where(Occupancy.guest_id == guest.id)
            .order_by(SubletRequest.created_at.desc())
        )
    )

    return [
        SubletRequestRead(
            id=sr.id,
            current_occupancy_id=sr.current_occupancy_id,
            proposed_renter_party_id=sr.proposed_renter_party_id,
            status=sr.status,
            authority_evidence_ref=sr.authority_evidence_ref,
            admin_decision=sr.admin_decision,
            admin_notes=sr.admin_notes,
            decided_by_admin_id=sr.decided_by_admin_id,
            created_at=sr.created_at,
            decided_at=sr.decided_at,
        )
        for sr in sublet_requests
    ]
