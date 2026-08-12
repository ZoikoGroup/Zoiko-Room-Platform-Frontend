from sqlalchemy.orm import Session

from app.models.admin_user import AdminUser
from app.models.audit import AuditEvent


def log_audit_event(
    db: Session,
    actor: AdminUser,
    action: str,
    resource_type: str,
    resource_id: str,
    correlation_id: str = "",
    reason: str = "",
) -> AuditEvent:
    event = AuditEvent(
        actor_admin_id=actor.id,
        role=actor.role,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        reason=reason,
        correlation_id=correlation_id,
    )
    db.add(event)
    db.flush()
    return event
