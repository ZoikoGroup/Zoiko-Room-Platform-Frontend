from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.review import Review
from app.schemas.review import ReviewRead


def list_reviews(db: Session) -> list[ReviewRead]:
    reviews = db.scalars(
        select(Review).options(joinedload(Review.listing), joinedload(Review.guest)).order_by(Review.date.desc())
    )
    return [to_review_read(r) for r in reviews]


def to_review_read(review: Review) -> ReviewRead:
    return ReviewRead(
        id=review.id,
        listing_id=review.listing_id,
        listing_name=review.listing.name,
        guest_name=review.guest.name,
        guest_avatar=review.guest.avatar,
        rating=review.rating,
        comment=review.comment,
        date=review.date,
        property_type=review.listing.property_type,
    )
