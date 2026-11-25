from modules.gateway.domain.entities import ProjectEntity
from modules.gateway.domain.interfaces import IProjectRepository


class ListProjectsUseCase:
    """Use case to retrieve registered projects scoped by admin or user membership."""

    def __init__(self, project_repo: IProjectRepository) -> None:
        self.project_repo = project_repo

    async def execute(
        self, user_id: int | None = None, is_admin: bool = False
    ) -> list[ProjectEntity]:
        if is_admin or user_id is None:
            return await self.project_repo.list_all()
        return await self.project_repo.list_by_user_id(user_id)
