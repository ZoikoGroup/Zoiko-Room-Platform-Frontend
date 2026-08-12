from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud.leasing import submit_application, to_application_read
from app.crud.listing import list_public_listings, to_public_listing_read
from app.db.session import get_db
from app.schemas.leasing import ApplicationCreate, ApplicationRead
from app.schemas.listing import PublicListingRead

router = APIRouter(prefix="/api/public", tags=["public"])


@router.get("/listings", response_model=list[PublicListingRead])
def get_public_listings(db: Session = Depends(get_db)):
    return [to_public_listing_read(listing) for listing in list_public_listings(db)]


@router.post("/applications", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def post_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    """No auth -- the separate renter-facing website submits directly on a renter's
    behalf, same as the existing new-guest booking flow."""
    return to_application_read(submit_application(db, payload))
