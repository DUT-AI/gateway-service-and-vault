import pytest
from sqlalchemy import select

from core.events.domain_event import DomainEvent
from core.events.models import OutboxEventModel
from core.events.outbox import SqlOutboxRepository
from core.events.processor import OutboxProcessor


@pytest.mark.asyncio
async def test_outbox_processor_handler_execution(db_session):
    """Verify that OutboxProcessor dispatches to registered handler and marks event PROCESSED."""
    repo = SqlOutboxRepository(db_session)
    event = DomainEvent(
        event_type="order.created",
        payload={"order_id": 123, "amount": 99.9},
    )
    await repo.save_event(event)

    received_payloads = []

    async def sample_handler(payload: dict):
        received_payloads.append(payload)

    processor = OutboxProcessor()
    processor.register_handler("order.created", sample_handler)

    count = await processor.process_pending_batch(db_session)
    assert count == 1
    assert len(received_payloads) == 1
    assert received_payloads[0]["order_id"] == 123

    # Verify event marked PROCESSED
    stmt = select(OutboxEventModel).where(OutboxEventModel.id == event.event_id)
    res = await db_session.execute(stmt)
    model = res.scalar_one()
    assert model.status == "PROCESSED"
    assert model.processed_at is not None


@pytest.mark.asyncio
async def test_outbox_processor_marks_failed_on_exception(db_session):
    """Verify that OutboxProcessor records failure and increments retry_count when handler raises."""
    repo = SqlOutboxRepository(db_session)
    event = DomainEvent(
        event_type="payment.failed",
        payload={"payment_id": 999},
    )
    await repo.save_event(event)

    async def failing_handler(payload: dict):
        raise ValueError("Network timeout connecting to payment gateway")

    processor = OutboxProcessor()
    processor.register_handler("payment.failed", failing_handler)

    count = await processor.process_pending_batch(db_session)
    assert count == 0

    # Verify event marked FAILED
    stmt = select(OutboxEventModel).where(OutboxEventModel.id == event.event_id)
    res = await db_session.execute(stmt)
    model = res.scalar_one()
    assert model.status == "FAILED"
    assert model.retry_count == 1
    assert "Network timeout" in (model.error_message or "")
