"""Use case for retrieving real-time service quota usage for a project."""

from modules.gateway.domain.interfaces import (
    IProjectRepository,
    IQuotaPolicyRepository,
    IQuotaUsageTracker,
)
from modules.gateway.dtos.gateway_dtos import QuotaUsageResponse
from modules.gateway.use_cases.exceptions import ServiceNotBoundError


class GetProjectServiceUsageUseCase:
    """Retrieves current day request count and quota consumption percentage."""

    def __init__(
        self,
        project_repo: IProjectRepository,
        quota_tracker: IQuotaUsageTracker,
        quota_repo: IQuotaPolicyRepository,
    ) -> None:
        self.project_repo = project_repo
        self.quota_tracker = quota_tracker
        self.quota_repo = quota_repo

    async def execute(self, project_id: str, service_id: str) -> QuotaUsageResponse:
        policy = await self.quota_repo.get_service_quota(project_id, service_id)
        if not policy:
            raise ServiceNotBoundError(
                f"Service '{service_id}' is not bound to project '{project_id}'"
            )

        usage = await self.quota_tracker.get_usage(project_id, service_id)
        pct = (
            round((usage / policy.quota_daily) * 100, 1)
            if policy.quota_daily > 0
            else 0.0
        )
        return QuotaUsageResponse(
            project_id=project_id,
            service_id=service_id,
            usage_today=usage,
            quota_daily=policy.quota_daily,
            rate_limit_rpm=policy.rate_limit_rpm,
            usage_percentage=pct,
            is_exhausted=usage >= policy.quota_daily,
        )
