from collections.abc import Generator

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, decode_access_token_claims
from app.crud.admin import get_admin_by_email
from app.crud.user import get_user_by_email
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.user_account import UserAccount

COOKIE_NAME = "zoiko_admin_token"
USER_COOKIE_NAME = "zoiko_user_token"


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


def get_current_user(
    zoiko_user_token: str | None = Cookie(default=None, alias=USER_COOKIE_NAME),
    db: Session = Depends(get_db),
) -> UserAccount:
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if not zoiko_user_token:
        raise unauthorized
    claims = decode_access_token_claims(zoiko_user_token)
    email = claims.get("sub") if claims else None
    if not email:
        raise unauthorized
    user = get_user_by_email(db, email)
    if not user or not user.is_active:
        raise unauthorized
    # A password reset stamps password_changed_at -- any token issued before that
    # moment (i.e. every session that existed at reset time) is rejected here,
    # forcing a fresh login. Rows created before this feature have no timestamp and
    # are unaffected.
    if user.password_changed_at is not None:
        issued_at = claims.get("iat") if claims else None
        if not isinstance(issued_at, (int, float)) or issued_at < user.password_changed_at.timestamp():
            raise unauthorized
    return user

