from modules.gateway.domain.entities import QuotaPolicyEntity, UpstreamServiceEntity
from modules.gateway.domain.interfaces import (
    IProjectRepository,
    IQuotaPolicyRepository,
    IUpstreamServiceRepository,
)
from modules.gateway.use_cases.exceptions import (
    ProjectNotFoundError,
    ServiceAlreadyBoundError,
    ServiceNotFoundError,
)


class BindServiceToProjectUseCase:
    """Use case to bind an upstream service to a project with quota policy."""

    def __init__(
        self,
        project_repo: IProjectRepository,
        service_repo: IUpstreamServiceRepository,
        quota_repo: IQuotaPolicyRepository,
    ) -> None:
        self.project_repo = project_repo
        self.service_repo = service_repo
        self.quota_repo = quota_repo

    async def execute(
        self,
        project_id: str,
        service_id: str,
        rate_limit_rpm: int = 60,
        quota_daily: int = 10000,
    ) -> tuple[UpstreamServiceEntity, QuotaPolicyEntity]:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project '{project_id}' not found")

        service = await self.service_repo.get_by_id(service_id)
        if not service:
            raise ServiceNotFoundError(f"Upstream service '{service_id}' not found")

        if await self.quota_repo.is_service_allowed(project_id, service_id):
            raise ServiceAlreadyBoundError(
                f"Service '{service_id}' is already bound to project '{project_id}'"
            )

        return await self.quota_repo.bind_service(
            project_id=project_id,
            service_id=service_id,
            rate_limit_rpm=rate_limit_rpm,
            quota_daily=quota_daily,
        )
