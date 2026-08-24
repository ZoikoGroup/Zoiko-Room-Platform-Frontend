import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

# (magic bytes, stored extension, canonical content type). Checked against the
# actual file contents -- never the filename extension or the client-declared
# Content-Type header, both of which are trivially spoofable.
_SIGNATURES: list[tuple[bytes, str, str]] = [
    (b"%PDF-", ".pdf", "application/pdf"),
    (b"\xff\xd8\xff", ".jpg", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", ".png", "image/png"),
]


def _sniff(contents: bytes) -> tuple[str, str] | None:
    for magic, extension, content_type in _SIGNATURES:
        if contents.startswith(magic):
            return extension, content_type
    return None


async def save_identity_document(file: UploadFile) -> tuple[str, str, str, int]:
    """Validates and persists an uploaded identity document outside any publicly
    served directory. Returns (stored_filename, original_filename, content_type, size).
    Only `stored_filename` (a random name with no relation to the upload) should
    ever be persisted to the database or used to build a path."""
    contents = await file.read()
    size = len(contents)

    if size == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The uploaded file is empty")

    max_bytes = settings.identity_document_max_size_mb * 1024 * 1024
    if size > max_bytes:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"File exceeds the {settings.identity_document_max_size_mb}MB limit",
        )

    sniffed = _sniff(contents)
    if not sniffed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported file — upload a PDF, JPG or PNG")
    extension, content_type = sniffed

    upload_dir = Path(settings.identity_upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid.uuid4().hex}{extension}"
    (upload_dir / stored_filename).write_bytes(contents)

    original_filename = Path(file.filename or "document").name
    return stored_filename, original_filename, content_type, size


def resolve_identity_document_path(stored_filename: str) -> Path:
    """`stored_filename` only ever originates from `save_identity_document` above
    (a uuid4 hex we generated), never from client input, so this can't be used
    for path traversal."""
    return Path(settings.identity_upload_dir) / stored_filename
