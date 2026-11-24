from modules.gateway.domain.interfaces import (
    IProjectRepository,
    IQuotaPolicyRepository,
)
from modules.gateway.use_cases.exceptions import (
    ProjectNotFoundError,
    ServiceNotBoundError,
)


class UnbindServiceFromProjectUseCase:
    """Use case to revoke/unbind an upstream service from a project."""

    def __init__(
        self,
        project_repo: IProjectRepository,
        quota_repo: IQuotaPolicyRepository,
    ) -> None:
        self.project_repo = project_repo
        self.quota_repo = quota_repo

    async def execute(self, project_id: str, service_id: str) -> None:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project '{project_id}' not found")

        unbound = await self.quota_repo.unbind_service(project_id, service_id)
        if not unbound:
            raise ServiceNotBoundError(
                f"Service '{service_id}' is not bound to project '{project_id}'"
            )
