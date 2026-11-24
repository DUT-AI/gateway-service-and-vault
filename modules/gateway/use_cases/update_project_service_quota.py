from modules.gateway.domain.entities import QuotaPolicyEntity
from modules.gateway.domain.interfaces import (
    IProjectRepository,
    IQuotaPolicyRepository,
)
from modules.gateway.use_cases.exceptions import (
    ProjectNotFoundError,
    ServiceNotBoundError,
)


class UpdateProjectServiceQuotaUseCase:
    """Use case to update traffic quota limits for a bound project service."""

    def __init__(
        self,
        project_repo: IProjectRepository,
        quota_repo: IQuotaPolicyRepository,
    ) -> None:
        self.project_repo = project_repo
        self.quota_repo = quota_repo

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

        if not await self.quota_repo.is_service_allowed(project_id, service_id):
            raise ServiceNotBoundError(
                f"Service '{service_id}' is not bound to project '{project_id}'"
            )

        return await self.quota_repo.update_service_quota(
            project_id=project_id,
            service_id=service_id,
            rate_limit_rpm=rate_limit_rpm,
            quota_daily=quota_daily,
        )
