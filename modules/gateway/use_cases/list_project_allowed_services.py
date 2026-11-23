from modules.gateway.domain.entities import QuotaPolicyEntity, UpstreamServiceEntity
from modules.gateway.domain.interfaces import IProjectRepository
from modules.gateway.use_cases.exceptions import ProjectNotFoundError


class ListProjectAllowedServicesUseCase:
    """Use case to list all upstream services allowed for a given project."""

    def __init__(self, project_repo: IProjectRepository) -> None:
        self.project_repo = project_repo

    async def execute(
        self, project_id: str
    ) -> list[tuple[UpstreamServiceEntity, QuotaPolicyEntity | None]]:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project '{project_id}' not found")

        return await self.project_repo.list_allowed_services(project_id)
