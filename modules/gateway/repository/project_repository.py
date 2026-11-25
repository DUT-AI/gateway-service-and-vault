from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.gateway.domain.entities import ProjectEntity
from modules.gateway.domain.interfaces import IProjectRepository
from modules.gateway.models.member import ProjectMemberModel
from modules.gateway.models.project import ProjectModel


class SqlProjectRepository(IProjectRepository):
    """Repository strictly responsible for Project aggregate root persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: ProjectModel) -> ProjectEntity:
        return ProjectEntity(
            id=model.id,
            name=model.name,
            slug=model.slug,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, project_id: str) -> ProjectEntity | None:
        stmt = select(ProjectModel).where(ProjectModel.id == project_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> ProjectEntity | None:
        stmt = select(ProjectModel).where(ProjectModel.slug == slug)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(
        self, name: str, slug: str, description: str | None = None
    ) -> ProjectEntity:
        model = ProjectModel(name=name, slug=slug, description=description)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def list_all(self) -> list[ProjectEntity]:
        stmt = select(ProjectModel).order_by(ProjectModel.created_at.desc())
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_by_user_id(self, user_id: int) -> list[ProjectEntity]:
        stmt = (
            select(ProjectModel)
            .join(ProjectMemberModel, ProjectMemberModel.project_id == ProjectModel.id)
            .where(ProjectMemberModel.user_id == user_id)
            .order_by(ProjectModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]
