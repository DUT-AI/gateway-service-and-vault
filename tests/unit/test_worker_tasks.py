import pytest

from apps.worker.main import send_welcome_email
from core.events.domain_event import DomainEvent
from core.events.outbox import SqlOutboxRepository


@pytest.mark.asyncio
async def test_worker_task_send_welcome_email():
    """Verify that send_welcome_email task executes successfully."""
    ctx = {}
    result = await send_welcome_email(ctx, user_id=42, email="worker_test@example.com")
    assert result is True


@pytest.mark.asyncio
async def test_outbox_event_lifecycle(db_session):
    """Verify Outbox repository persistence, querying, and marking processed."""
    repo = SqlOutboxRepository(db_session)

    # 1. Save new domain event
    event = DomainEvent(
        event_type="user.created",
        payload={"user_id": 1, "email": "event@example.com"},
    )
    await repo.save_event(event)

    # 2. Fetch pending events
    pending = await repo.fetch_pending_events(limit=10)
    assert len(pending) >= 1
    found = next((e for e in pending if e.id == event.event_id), None)
    assert found is not None
    assert found.event_type == "user.created"
    assert found.status == "PENDING"

    # 3. Mark processed
    await repo.mark_processed(event.event_id)
    pending_after = await repo.fetch_pending_events(limit=10)
    assert not any(e.id == event.event_id for e in pending_after)
