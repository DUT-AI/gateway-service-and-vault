from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base, TimestampMixin, ULIDPrimaryKeyMixin


class SecretItemModel(Base, ULIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for encrypted secret key-value items."""

    __tablename__ = "secrets"

    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    scope_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("secret_scopes.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    encrypted_value: Mapped[str] = mapped_column(Text, nullable=False)
    nonce: Mapped[str] = mapped_column(String(32), nullable=False)
    auth_tag: Mapped[str] = mapped_column(String(32), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    updated_by: Mapped[str] = mapped_column(String(100), default="", nullable=False)

    # Relationships
    scope = relationship("SecretScopeModel", back_populates="secrets")
    history = relationship(
        "SecretHistoryModel",
        back_populates="secret",
        cascade="all, delete-orphan",
    )

    __table_args__ = (UniqueConstraint("scope_id", "key", name="uq_secret_scope_key"),)


class SecretHistoryModel(Base, ULIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for secret version history."""

    __tablename__ = "secret_histories"

    secret_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("secrets.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    encrypted_value: Mapped[str] = mapped_column(Text, nullable=False)
    nonce: Mapped[str] = mapped_column(String(32), nullable=False)
    auth_tag: Mapped[str] = mapped_column(String(32), nullable=False)
    modified_by: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    secret = relationship("SecretItemModel", back_populates="history")
