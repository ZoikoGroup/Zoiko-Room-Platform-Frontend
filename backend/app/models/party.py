from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

PARTY_TYPES = ("provider", "renter", "institution", "zoiko_operator")
PARTY_STATUSES = ("active", "suspended", "closed")


class Party(Base):
    __tablename__ = "parties"

    id: Mapped[int] = mapped_column(primary_key=True)
    party_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    jurisdiction: Mapped[str] = mapped_column(String(50), default="IN")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    memberships: Mapped[list["Membership"]] = relationship(back_populates="party", cascade="all, delete-orphan")
    properties: Mapped[list["Property"]] = relationship(back_populates="owner_party")
