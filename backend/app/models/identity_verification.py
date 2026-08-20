from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

IDENTITY_STATUSES = ("pending", "verified", "rejected", "expired", "additional_evidence_required")

DOCUMENT_TYPES = ("aadhaar", "passport", "driving_license")


class IdentityVerification(Base):
    __tablename__ = "identity_verifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    party_id: Mapped[int] = mapped_column(ForeignKey("parties.id", ondelete="CASCADE"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    encrypted_reference: Mapped[str] = mapped_column(String(1024), nullable=False)
    evidence_ref: Mapped[str] = mapped_column(String(1024), default="")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verifier_admin_id: Mapped[int | None] = mapped_column(ForeignKey("admin_users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    party: Mapped["Party"] = relationship(back_populates="identity_verifications")
    verifier_admin: Mapped["AdminUser"] = relationship()
