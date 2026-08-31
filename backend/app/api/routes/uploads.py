from fastapi import APIRouter, Depends, UploadFile

from app.api.deps import get_current_admin
from app.core.image_uploads import save_listing_images

router = APIRouter(prefix="/api/uploads", tags=["uploads"], dependencies=[Depends(get_current_admin)])


@router.post("/images")
async def upload_images(files: list[UploadFile]):
    urls = await save_listing_images(files)
    return {"urls": urls}
