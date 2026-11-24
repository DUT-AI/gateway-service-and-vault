from modules.gateway.domain.entities import QuotaPolicyEntity, UpstreamServiceEntity
from modules.gateway.domain.interfaces import (
    IProjectRepository,
    IQuotaPolicyRepository,
)
from modules.gateway.use_cases.exceptions import ProjectNotFoundError


class ListProjectAllowedServicesUseCase:
    """Use case to list all upstream services allowed for a given project."""

    def __init__(
        self,
        project_repo: IProjectRepository,
        quota_repo: IQuotaPolicyRepository,
    ) -> None:
        self.project_repo = project_repo
        self.quota_repo = quota_repo

    async def execute(
        self, project_id: str
    ) -> list[tuple[UpstreamServiceEntity, QuotaPolicyEntity | None]]:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project '{project_id}' not found")

        return await self.quota_repo.list_allowed_services(project_id)
