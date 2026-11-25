from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base, TimestampMixin, ULIDPrimaryKeyMixin

# Many-to-many relationship table between projects and upstream services
project_upstream_association = Table(
    "project_upstream_allowlist",
    Base.metadata,
    Column(
        "project_id",
        String(26),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "service_id",
        String(26),
        ForeignKey("upstream_services.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ProjectModel(Base, ULIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for projects."""

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    allowed_services = relationship(
        "UpstreamServiceModel",
        secondary=project_upstream_association,
        back_populates="allowed_projects",
    )
    virtual_keys = relationship(
        "VirtualAccessKeyModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    quota_policies = relationship(
        "QuotaPolicyModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    members = relationship(
        "ProjectMemberModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )
