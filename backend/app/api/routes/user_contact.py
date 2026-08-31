from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.contact_email import create_contact_email
from app.db.session import get_db
from app.models.user_account import UserAccount
from app.schemas.contact_email import ContactEmailRead

router = APIRouter(prefix="/api/users/contact", tags=["contact-admin"], dependencies=[Depends(get_current_user)])


class _SendRequest(BaseModel):
    subject: str
    message: str


@router.post("", response_model=ContactEmailRead, status_code=status.HTTP_201_CREATED)
def send_to_admin(
    payload: _SendRequest,
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject = payload.subject.strip()
    message = payload.message.strip()
    if not subject:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Subject is required")
    if not message:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Message is required")
    if len(subject) > 255:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Subject must be 255 characters or fewer")

    email = create_contact_email(db, user.id, subject, message)
    return ContactEmailRead(
        id=email.id,
        user_id=email.user_id,
        subject=email.subject,
        message=email.message,
        is_read=email.is_read,
        created_at=email.created_at.isoformat(),
        user_email=user.email,
        user_name=user.full_name,
    )
