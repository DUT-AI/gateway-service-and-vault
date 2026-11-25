from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base, TimestampMixin, ULIDPrimaryKeyMixin


class ProjectMemberModel(Base, ULIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for Project Membership binding SSO user IDs to projects."""

    __tablename__ = "project_members"

    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    added_by: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    project = relationship("ProjectModel", back_populates="members")

    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_member_user"),
        Index("ix_project_members_user_id", "user_id"),
    )
