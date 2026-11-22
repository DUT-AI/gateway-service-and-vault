from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.events.domain_event import DomainEvent
from core.events.models import OutboxEventModel
from core.utils.datetime_utils import now_utc


class IOutboxRepository(Protocol):
    """Protocol for Outbox persistence."""

    async def save_event(self, event: DomainEvent) -> None:
        """Persist domain event to outbox table."""
        ...

    async def fetch_pending_events(self, limit: int = 50) -> list[OutboxEventModel]:
        """Fetch pending events for processing."""
        ...

    async def mark_processed(self, event_id: str) -> None:
        """Mark an outbox event as PROCESSED."""
        ...

    async def mark_failed(self, event_id: str, error_message: str) -> None:
        """Mark an outbox event as FAILED with error message."""
        ...


class SqlOutboxRepository(IOutboxRepository):
    """SQLAlchemy implementation of outbox event repository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_event(self, event: DomainEvent) -> None:
        outbox_event = OutboxEventModel(
            id=event.event_id,
            event_type=event.event_type,
            payload=event.payload,
            status="PENDING",
            created_at=event.occurred_at,
        )
        self.session.add(outbox_event)
        await self.session.flush()

    async def fetch_pending_events(self, limit: int = 50) -> list[OutboxEventModel]:
        stmt = (
            select(OutboxEventModel)
            .where(OutboxEventModel.status == "PENDING")
            .order_by(OutboxEventModel.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_processed(self, event_id: str) -> None:
        stmt = select(OutboxEventModel).where(OutboxEventModel.id == event_id)
        result = await self.session.execute(stmt)
        event = result.scalar_one_or_none()
        if event:
            event.status = "PROCESSED"
            event.processed_at = now_utc()
            await self.session.flush()

    async def mark_failed(self, event_id: str, error_message: str) -> None:
        stmt = select(OutboxEventModel).where(OutboxEventModel.id == event_id)
        result = await self.session.execute(stmt)
        event = result.scalar_one_or_none()
        if event:
            event.status = "FAILED"
            event.error_message = error_message[:1024]
            event.retry_count += 1
            await self.session.flush()
