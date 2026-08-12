import secrets
from urllib.parse import quote


def new_id(prefix: str) -> str:
    return f"{prefix}-{secrets.token_hex(4).upper()}"


def slugify(name: str) -> str:
    import re

    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or new_id("listing").lower()


def dicebear_avatar(name: str) -> str:
    return f"https://api.dicebear.com/9.x/notionists/svg?seed={quote(name)}&backgroundColor=eef2fa,fdecec"
