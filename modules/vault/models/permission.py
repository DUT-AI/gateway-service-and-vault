from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.database.base import Base, TimestampMixin, ULIDPrimaryKeyMixin


class KeyPermissionModel(Base, ULIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for granular identity-to-key secret permissions."""

    __tablename__ = "key_permissions"

    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    identity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    identity_type: Mapped[str] = mapped_column(
        String(20), default="client", nullable=False
    )
    secret_key: Mapped[str] = mapped_column(String(100), nullable=False)
    granted_by: Mapped[str] = mapped_column(String(100), default="", nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "project_id", "identity_id", "secret_key", name="uq_project_identity_key"
        ),
        Index("ix_key_permissions_lookup", "project_id", "identity_id"),
    )
