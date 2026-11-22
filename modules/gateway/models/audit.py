from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database.base import Base, ULIDPrimaryKeyMixin


class AuditEventModel(Base, ULIDPrimaryKeyMixin):
    """SQLAlchemy model for immutable security and access audit logs."""

    __tablename__ = "audit_events"

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True,
        nullable=False,
    )
    client_type: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    project_id: Mapped[str] = mapped_column(String(26), index=True, nullable=False)
    service_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    action: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    decision: Mapped[str] = mapped_column(String(10), nullable=False)  # ALLOW, DENY
    client_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )
