from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base, TimestampMixin, ULIDPrimaryKeyMixin


class RegisteredClientModel(Base, ULIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for registered clients (User Devices & App Servers)."""

    __tablename__ = "registered_clients"

    client_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # USER_DEVICE, APP_SERVER
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    cert_fingerprint: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    cert_serial: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    virtual_keys = relationship(
        "VirtualAccessKeyModel",
        back_populates="client",
        cascade="all, delete-orphan",
    )
    quota_policies = relationship(
        "QuotaPolicyModel",
        back_populates="client",
        cascade="all, delete-orphan",
    )
