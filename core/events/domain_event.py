from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from core.utils.id_generator import generate_ulid


@dataclass
class DomainEvent:
    """Base domain event class."""

    event_type: str
    payload: dict[str, Any]
    event_id: str = field(default_factory=generate_ulid)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
