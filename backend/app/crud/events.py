from sqlalchemy.orm import Session

from app.models.domain_event import DomainEvent


def emit_event(db: Session, event_type: str, resource_type: str, resource_id: str, payload: dict | None = None) -> DomainEvent:
    """Append a domain event row within the same transaction as the mutation that caused
    it, so it's only ever visible once that transaction commits. No async consumer is
    wired up yet -- this is the outbox scaffold described in Phase 1 of the roadmap."""
    event = DomainEvent(
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        payload=payload or {},
    )
    db.add(event)
    db.flush()
    return event
