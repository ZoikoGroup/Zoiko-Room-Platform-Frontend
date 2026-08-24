from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings

# Mirrors Django's/Rails' well-known file-based email backends: no real SMTP
# provider is configured for this project, so in non-production runs the email is
# written to a local outbox file instead of being sent. This is a dev-testing aid,
# not a fake production send path -- nothing here is written through the
# application's request/audit logging, and the branch is a hard no-op once
# COOKIE_SECURE=true (i.e. once this looks like a real deployment).
DEV_MAIL_OUTBOX_DIR = Path("dev_mail_outbox")


def send_password_reset_email(to_email: str, reset_link: str, expires_minutes: int) -> None:
    if settings.cookie_secure:
        # No real email provider is wired up yet. Wire one up (SES/SendGrid/etc.)
        # here before relying on this in production -- deliberately not faking it.
        return

    DEV_MAIL_OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in "@.-_" else "_" for c in to_email)
    outbox_file = DEV_MAIL_OUTBOX_DIR / f"{safe_name}.txt"
    outbox_file.write_text(
        "This file is a local development mail outbox entry, not a sent email.\n"
        f"To: {to_email}\n"
        f"Generated at: {datetime.now(timezone.utc).isoformat()}\n"
        "Subject: Reset your Zoiko Rooms password\n\n"
        f"Reset link (valid {expires_minutes} minutes): {reset_link}\n",
        encoding="utf-8",
    )
