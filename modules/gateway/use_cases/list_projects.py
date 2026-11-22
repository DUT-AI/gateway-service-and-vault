from modules.gateway.domain.entities import ProjectEntity
from modules.gateway.domain.interfaces import IProjectRepository


class ListProjectsUseCase:
    """Use case to retrieve all registered projects."""

    def __init__(self, project_repo: IProjectRepository) -> None:
        self.project_repo = project_repo

    async def execute(self) -> list[ProjectEntity]:
        return await self.project_repo.list_all()
