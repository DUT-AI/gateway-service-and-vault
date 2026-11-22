from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base, TimestampMixin, ULIDPrimaryKeyMixin


class VirtualAccessKeyModel(Base, ULIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for Virtual Access Keys bound to client and project."""

    __tablename__ = "virtual_access_keys"

    key_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    key_prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    client_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("registered_clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    client = relationship("RegisteredClientModel", back_populates="virtual_keys")
    project = relationship("ProjectModel", back_populates="virtual_keys")

    __table_args__ = (
        Index("ix_virtual_keys_client_project", "client_id", "project_id"),
    )
