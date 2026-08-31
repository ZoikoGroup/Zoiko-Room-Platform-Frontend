from datetime import datetime

from app.schemas.common import CamelModel


class NotificationRead(CamelModel):
    id: int
    title: str
    message: str
    notification_type: str
    related_entity_type: str
    related_entity_id: str
    is_read: bool
    created_at: datetime
    read_at: datetime | None


class UnreadCountRead(CamelModel):
    count: int
