from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.gateway.domain.entities import ProjectMemberEntity
from modules.gateway.domain.interfaces import IProjectMemberRepository
from modules.gateway.models.member import ProjectMemberModel


class SqlProjectMemberRepository(IProjectMemberRepository):
    """Repository strictly responsible for ProjectMember aggregate root persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: ProjectMemberModel) -> ProjectMemberEntity:
        return ProjectMemberEntity(
            id=model.id,
            project_id=model.project_id,
            user_id=model.user_id,
            added_by=model.added_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def add_member(
        self, project_id: str, user_id: int, added_by: int
    ) -> ProjectMemberEntity:
        stmt = select(ProjectMemberModel).where(
            ProjectMemberModel.project_id == project_id,
            ProjectMemberModel.user_id == user_id,
        )
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            model = ProjectMemberModel(
                project_id=project_id,
                user_id=user_id,
                added_by=added_by,
            )
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
        return self._to_entity(model)

    async def remove_member(self, project_id: str, user_id: int) -> bool:
        stmt = delete(ProjectMemberModel).where(
            ProjectMemberModel.project_id == project_id,
            ProjectMemberModel.user_id == user_id,
        )
        res = await self.session.execute(stmt)
        await self.session.flush()
        return bool(res.rowcount and res.rowcount > 0)

    async def list_members(self, project_id: str) -> list[ProjectMemberEntity]:
        stmt = (
            select(ProjectMemberModel)
            .where(ProjectMemberModel.project_id == project_id)
            .order_by(ProjectMemberModel.created_at.asc())
        )
        res = await self.session.execute(stmt)
        return [self._to_entity(m) for m in res.scalars().all()]

    async def is_member(self, project_id: str, user_id: int) -> bool:
        stmt = select(ProjectMemberModel.id).where(
            ProjectMemberModel.project_id == project_id,
            ProjectMemberModel.user_id == user_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none() is not None
