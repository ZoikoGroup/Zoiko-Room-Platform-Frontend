from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_super_admin
from app.crud.review import list_reviews
from app.db.session import get_db
from app.schemas.review import ReviewRead

router = APIRouter(prefix="/api/reviews", tags=["reviews"], dependencies=[Depends(require_super_admin)])


@router.get("", response_model=list[ReviewRead])
def get_reviews(db: Session = Depends(get_db)):
    return list_reviews(db)
