from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

SUBLET_REQUEST_STATUSES = ("pending_verification", "pending_admin_review", "approved", "rejected")


class SubletRequest(Base):
    """Tracks a request from a current renter to sublet their occupancy to a new renter."""

    __tablename__ = "sublet_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    current_occupancy_id: Mapped[int] = mapped_column(ForeignKey("occupancies.id", ondelete="CASCADE"), unique=True, nullable=False)
    proposed_renter_party_id: Mapped[int] = mapped_column(ForeignKey("parties.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending_verification", index=True)
    authority_evidence_ref: Mapped[str] = mapped_column(String(1024), default="")
    admin_decision: Mapped[str] = mapped_column(String(20), default="")
    admin_notes: Mapped[str] = mapped_column(String(2000), default="")
    decided_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("admin_users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    current_occupancy: Mapped["Occupancy"] = relationship()
    proposed_renter_party: Mapped["Party"] = relationship()
    decided_by_admin: Mapped["AdminUser"] = relationship()
