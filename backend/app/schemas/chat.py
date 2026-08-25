from datetime import datetime

from app.schemas.common import CamelModel


class ChatConversationRead(CamelModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class ChatMessageRead(CamelModel):
    id: int
    role: str
    content: str
    created_at: datetime


class ChatSendMessageRequest(CamelModel):
    content: str
