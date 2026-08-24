from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_expire_minutes)
    # "iat" (issued-at, as an int epoch so decoding never depends on jose's
    # datetime-claim handling) lets USER sessions be invalidated after a password
    # reset without a server-side token blacklist -- see get_current_user. Admin
    # tokens carry it too since the two auth flows share this helper, but the
    # admin decode path below only ever reads "sub", so it has no effect there.
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token_claims(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None


def decode_access_token(token: str) -> str | None:
    claims = decode_access_token_claims(token)
    return claims.get("sub") if claims else None
