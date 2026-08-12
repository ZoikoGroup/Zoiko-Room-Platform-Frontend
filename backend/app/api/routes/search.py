from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.crud.search import global_search
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.search import SearchResult

router = APIRouter(prefix="/api/search", tags=["search"], dependencies=[Depends(get_current_admin)])


@router.get("", response_model=list[SearchResult])
def search(q: str, admin: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = q.strip()
    if len(query) < 2:
        return []
    return global_search(db, admin, query)
