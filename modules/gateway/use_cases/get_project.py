from modules.gateway.domain.entities import ProjectEntity
from modules.gateway.domain.interfaces import IProjectRepository
from modules.gateway.use_cases.exceptions import ProjectNotFoundError


class GetProjectUseCase:
    """Use case to retrieve a single project by its ID."""

    def __init__(self, project_repo: IProjectRepository) -> None:
        self.project_repo = project_repo

    async def execute(self, project_id: str) -> ProjectEntity:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project '{project_id}' not found")
        return project
