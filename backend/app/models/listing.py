from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Private-room-only per the marketplace standard. Kept as a column (rather than dropped)
# because bookings/reviews/analytics/search -- explicitly out of scope for this pass --
# still read it; new listings are constrained to "private_room" at the API layer.
PROPERTY_TYPES = ("private_room",)

LISTING_STATES = ("DRAFT", "EVIDENCE_PENDING", "REVIEW", "PUBLISHED", "PAUSED", "SUSPENDED", "WITHDRAWN", "ARCHIVED")


class Listing(Base):
    __tablename__ = "listings"
    # 0001_initial.py created a table-level UNIQUE constraint on slug plus a
    # separately named plain index (not a combined unique index) -- declared
    # explicitly here, matching the two real objects in the database, so
    # `alembic check` doesn't report a phantom constraint-vs-index diff.
    __table_args__ = (
        UniqueConstraint("slug", name="listings_slug_key"),
        Index("ix_listings_slug", "slug"),
    )

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    property_type: Mapped[str] = mapped_column(String(20), default="private_room")
    room_type: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_per_night: Mapped[float] = mapped_column(Float, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=4.5)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    guests: Mapped[int] = mapped_column(Integer, nullable=False)
    bedrooms: Mapped[int] = mapped_column(Integer, default=0)
    bathrooms: Mapped[int] = mapped_column(Integer, default=1)
    size: Mapped[int] = mapped_column(Integer, default=0)
    images: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    amenities: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    description: Mapped[str] = mapped_column(String(2000), default="")
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    # Admin-created listings retain their admin owner. USER-hosted listings are
    # owned by their Party and deliberately do not require an AdminUser account.
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("admin_users.id"), nullable=True)
    party_id: Mapped[int | None] = mapped_column(
        ForeignKey("parties.id", ondelete="CASCADE"), nullable=True, index=True
    )

    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    market_release_id: Mapped[int | None] = mapped_column(ForeignKey("market_releases.id"), nullable=True)
    min_stay_nights: Mapped[int] = mapped_column(Integer, default=30)
    state: Mapped[str] = mapped_column(String(20), default="DRAFT")

    # Optional per-listing override of the owner account's contact details --
    # left blank, the public API falls back to the owner's name/email/phone.
    contact_name: Mapped[str] = mapped_column(String(255), default="")
    contact_phone: Mapped[str] = mapped_column(String(50), default="")
    contact_email: Mapped[str] = mapped_column(String(255), default="")

    owner: Mapped["AdminUser"] = relationship(back_populates="listings")
    party: Mapped["Party"] = relationship(back_populates="listings")
    room: Mapped["Room"] = relationship(back_populates="listings")
    market_release: Mapped["MarketRelease"] = relationship(back_populates="listings")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="listing")
    reviews: Mapped[list["Review"]] = relationship(back_populates="listing")
