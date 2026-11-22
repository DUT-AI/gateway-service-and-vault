from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base, TimestampMixin, ULIDPrimaryKeyMixin


class QuotaPolicyModel(Base, ULIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for rate limiting and usage quota policies."""

    __tablename__ = "quota_policies"

    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    service_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("upstream_services.id", ondelete="CASCADE"),
        nullable=False,
    )
    client_id: Mapped[str | None] = mapped_column(
        String(26),
        ForeignKey("registered_clients.id", ondelete="CASCADE"),
        nullable=True,
    )
    rate_limit_rpm: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    quota_daily: Mapped[int] = mapped_column(Integer, default=10000, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    project = relationship("ProjectModel", back_populates="quota_policies")
    service = relationship("UpstreamServiceModel", back_populates="quota_policies")
    client = relationship("RegisteredClientModel", back_populates="quota_policies")
