from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud import notification as crud
from app.db.session import get_db
from app.models.user_account import UserAccount
from app.schemas.notification import NotificationRead, UnreadCountRead

router = APIRouter(prefix="/api/users/notifications", tags=["user-notifications"])


@router.get("", response_model=list[NotificationRead])
def list_notifications(user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    """Only ever the authenticated user's own notifications -- filtered by
    recipient_user_id on the backend, never trusted from the client."""
    return crud.list_for_user(db, user.id)


@router.get("/unread-count", response_model=UnreadCountRead)
def get_unread_count(user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    return UnreadCountRead(count=crud.count_unread_for_user(db, user.id))


@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_read(notification_id: int, user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = crud.mark_read_for_user(db, notification_id, user.id)
    if not notification:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
    return notification


@router.patch("/read-all")
def mark_all_read(user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    updated = crud.mark_all_read_for_user(db, user.id)
    return {"updated": updated}
