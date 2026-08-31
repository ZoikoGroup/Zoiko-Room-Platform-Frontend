from app.schemas.common import CamelModel


class ContactEmailCreate(CamelModel):
    subject: str
    message: str


class ContactEmailRead(CamelModel):
    id: int
    user_id: int
    subject: str
    message: str
    is_read: bool
    created_at: str
    user_email: str = ""
    user_name: str = ""
