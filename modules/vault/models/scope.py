from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base, TimestampMixin, ULIDPrimaryKeyMixin


class SecretScopeModel(Base, ULIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for secret scopes (e.g. Common, Financial, Auth-Core)."""

    __tablename__ = "secret_scopes"

    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    secrets = relationship(
        "SecretItemModel",
        back_populates="scope",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_scope_project_name"),
    )
