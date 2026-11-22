from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base, TimestampMixin, ULIDPrimaryKeyMixin
from modules.gateway.models.project import project_upstream_association


class UpstreamServiceModel(Base, ULIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for upstream API services."""

    __tablename__ = "upstream_services"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    auth_type: Mapped[str] = mapped_column(
        String(30), default="BEARER_TOKEN", nullable=False
    )
    encrypted_credential: Mapped[str] = mapped_column(Text, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    allowed_projects = relationship(
        "ProjectModel",
        secondary=project_upstream_association,
        back_populates="allowed_services",
    )
    quota_policies = relationship(
        "QuotaPolicyModel",
        back_populates="service",
        cascade="all, delete-orphan",
    )
