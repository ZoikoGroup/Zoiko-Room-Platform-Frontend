import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.api.deps import get_current_admin
from app.core.config import settings

router = APIRouter(prefix="/api/uploads", tags=["uploads"], dependencies=[Depends(get_current_admin)])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@router.post("/images")
async def upload_images(files: list[UploadFile]):
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    max_bytes = settings.max_upload_size_mb * 1024 * 1024

    urls: list[str] = []
    for file in files:
        extension = Path(file.filename or "").suffix.lower()
        if extension not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"'{file.filename}' isn't a supported image type (jpg, png, webp, gif only)",
            )

        contents = await file.read()
        if len(contents) > max_bytes:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"'{file.filename}' is larger than {settings.max_upload_size_mb}MB",
            )

        filename = f"{uuid.uuid4().hex}{extension}"
        (upload_dir / filename).write_bytes(contents)
        urls.append(f"{settings.public_api_url}/uploads/{filename}")

    return {"urls": urls}
