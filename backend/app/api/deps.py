from collections.abc import Generator

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.crud.admin import get_admin_by_email
from app.db.session import get_db
from app.models.admin_user import AdminUser

COOKIE_NAME = "zoiko_admin_token"


def get_current_admin(
    zoiko_admin_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
    db: Session = Depends(get_db),
) -> AdminUser:
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if not zoiko_admin_token:
        raise unauthorized
    email = decode_access_token(zoiko_admin_token)
    if not email:
        raise unauthorized
    admin = get_admin_by_email(db, email)
    if not admin or not admin.is_active or admin.approval_status != "approved":
        raise unauthorized
    return admin


def require_super_admin(admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
    if admin.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super admin access required")
    return admin
