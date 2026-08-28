from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.crud.contact_email import count_unread_contact_emails, get_contact_email, list_contact_emails, mark_contact_email_read
from app.db.session import get_db
from app.schemas.contact_email import ContactEmailRead

router = APIRouter(prefix="/api/admin/contact-emails", tags=["contact-admin"], dependencies=[Depends(get_current_admin)])


def _to_read(e) -> ContactEmailRead:
    return ContactEmailRead(
        id=e.id,
        user_id=e.user_id,
        subject=e.subject,
        message=e.message,
        is_read=e.is_read,
        created_at=e.created_at.isoformat(),
        user_email=e.user.email if e.user else "",
        user_name=e.user.full_name if e.user else "",
    )


@router.get("", response_model=list[ContactEmailRead])
def list_emails(unread: bool = False, db: Session = Depends(get_db)):
    return [_to_read(e) for e in list_contact_emails(db, unread_only=unread)]


@router.get("/unread-count")
def unread_count(db: Session = Depends(get_db)):
    return {"count": count_unread_contact_emails(db)}


@router.put("/{email_id}/read", response_model=ContactEmailRead)
def mark_read(email_id: int, db: Session = Depends(get_db)):
    email = mark_contact_email_read(db, email_id)
    if not email:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Email not found")
    return _to_read(email)
