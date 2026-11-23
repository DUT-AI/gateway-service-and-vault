from modules.gateway.domain.entities import QuotaPolicyEntity
from modules.gateway.domain.interfaces import IProjectRepository
from modules.gateway.use_cases.exceptions import (
    ProjectNotFoundError,
)


class UpdateProjectServiceQuotaUseCase:
    """Use case to update traffic quota limits for a bound project service."""

    def __init__(self, project_repo: IProjectRepository) -> None:
        self.project_repo = project_repo

    async def execute(
        self,
        project_id: str,
        service_id: str,
        rate_limit_rpm: int,
        quota_daily: int,
    ) -> QuotaPolicyEntity:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project '{project_id}' not found")

        return await self.project_repo.update_service_quota(
            project_id=project_id,
            service_id=service_id,
            rate_limit_rpm=rate_limit_rpm,
            quota_daily=quota_daily,
        )
