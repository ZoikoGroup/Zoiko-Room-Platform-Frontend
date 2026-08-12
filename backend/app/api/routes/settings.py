from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.crud.admin import get_or_create_settings, update_branding, update_notifications, update_profile
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.auth import AdminRead
from app.schemas.settings import BrandingRead, BrandingUpdate, NotificationsRead, NotificationsUpdate, ProfileUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"], dependencies=[Depends(get_current_admin)])


@router.get("/branding", response_model=BrandingRead)
def get_branding(admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    return get_or_create_settings(db, admin)


@router.put("/branding", response_model=BrandingRead)
def put_branding(payload: BrandingUpdate, admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    return update_branding(db, admin, payload.logo_url)


@router.put("/profile", response_model=AdminRead)
def put_profile(payload: ProfileUpdate, admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    return update_profile(db, admin, payload.full_name, payload.email, payload.phone)


@router.get("/notifications", response_model=NotificationsRead)
def get_notifications(admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    settings_row = get_or_create_settings(db, admin)
    return NotificationsRead(
        new_booking=settings_row.notify_new_booking,
        payments=settings_row.notify_payments,
        reviews=settings_row.notify_reviews,
        marketing=settings_row.notify_marketing,
    )


@router.put("/notifications", response_model=NotificationsRead)
def put_notifications(payload: NotificationsUpdate, admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    settings_row = update_notifications(db, admin, payload.new_booking, payload.payments, payload.reviews, payload.marketing)
    return NotificationsRead(
        new_booking=settings_row.notify_new_booking,
        payments=settings_row.notify_payments,
        reviews=settings_row.notify_reviews,
        marketing=settings_row.notify_marketing,
    )
