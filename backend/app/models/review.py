from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    listing_id: Mapped[str] = mapped_column(ForeignKey("listings.id"), nullable=False)
    guest_id: Mapped[str] = mapped_column(ForeignKey("guests.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(String(2000), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    listing: Mapped["Listing"] = relationship(back_populates="reviews")
    guest: Mapped["Guest"] = relationship(back_populates="reviews")
