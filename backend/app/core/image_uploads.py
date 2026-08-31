import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.models.listing import MAX_LISTING_IMAGES

# Checked against the actual file bytes -- never the filename extension or the
# client-declared Content-Type header, both of which are trivially spoofable.
# Mirrors the approach in core/identity_uploads.py.
_JPEG = b"\xff\xd8\xff"
_PNG = b"\x89PNG\r\n\x1a\n"
_GIF87A = b"GIF87a"
_GIF89A = b"GIF89a"


def _sniff_image_extension(contents: bytes) -> str | None:
    if contents.startswith(_JPEG):
        return ".jpg"
    if contents.startswith(_PNG):
        return ".png"
    if contents.startswith(_GIF87A) or contents.startswith(_GIF89A):
        return ".gif"
    if contents[:4] == b"RIFF" and contents[8:12] == b"WEBP":
        return ".webp"
    return None


async def save_listing_image(file: UploadFile) -> str:
    """Validates and stores one listing/property photo in the PUBLIC upload_dir,
    returning its public /uploads URL. Shared by the admin (`/api/uploads/images`)
    and USER hosting (`/api/users/hosting/uploads/images`) endpoints -- never for
    identity documents, which use their own private storage and directory
    (see identity_uploads.py); the two must never share a directory or endpoint."""
    contents = await file.read()
    if not contents:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"'{file.filename}' is empty")

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"'{file.filename}' is larger than {settings.max_upload_size_mb}MB",
        )

    extension = _sniff_image_extension(contents)
    if not extension:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"'{file.filename}' isn't a supported image type (jpg, png, webp, gif only)",
        )

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    # Random, server-generated filename -- the client's original filename is
    # never used to build a path or persisted anywhere.
    filename = f"{uuid.uuid4().hex}{extension}"
    (upload_dir / filename).write_bytes(contents)

    # Deliberately relative, not settings.public_api_url + "/uploads/..." --
    # that setting is an independently-configured backend env var that can (and,
    # in this project's dev environment, did) drift from the frontend's own
    # NEXT_PUBLIC_API_URL, baking a wrong/stale origin permanently into stored
    # listing data. The frontend resolves this path against whichever origin
    # it's actually configured to talk to (see resolveImageUrl in lib/utils.ts).
    return f"/uploads/{filename}"


async def save_listing_images(files: list[UploadFile]) -> list[str]:
    if len(files) > MAX_LISTING_IMAGES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"You can upload at most {MAX_LISTING_IMAGES} images at a time",
        )
    return [await save_listing_image(file) for file in files]
