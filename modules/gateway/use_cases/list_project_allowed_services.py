from dataclasses import dataclass
from datetime import datetime

from modules.gateway.domain.interfaces import (
    IProjectRepository,
    IQuotaPolicyRepository,
    IQuotaUsageTracker,
)
from modules.gateway.use_cases.exceptions import ProjectNotFoundError


@dataclass(frozen=True)
class AllowedServiceUsageDTO:
    service_id: str
    service_name: str
    service_slug: str
    base_url: str
    auth_type: str
    is_service_active: bool
    rate_limit_rpm: int
    quota_daily: int
    is_quota_active: bool
    usage_today: int
    usage_percentage: float
    bound_at: datetime | None


class ListProjectAllowedServicesUseCase:
    """Use case to list all upstream services allowed for a given project with real-time usage metrics."""

    def __init__(
        self,
        project_repo: IProjectRepository,
        quota_repo: IQuotaPolicyRepository,
        quota_tracker: IQuotaUsageTracker,
    ) -> None:
        self.project_repo = project_repo
        self.quota_repo = quota_repo
        self.quota_tracker = quota_tracker

    async def execute(self, project_id: str) -> list[AllowedServiceUsageDTO]:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project '{project_id}' not found")

        items = await self.quota_repo.list_allowed_services(project_id)
        results: list[AllowedServiceUsageDTO] = []
        for svc, quota in items:
            daily = quota.quota_daily if quota else 10000
            usage = await self.quota_tracker.get_usage(project_id, svc.id)
            pct = round((usage / daily) * 100, 1) if daily > 0 else 0.0
            results.append(
                AllowedServiceUsageDTO(
                    service_id=svc.id,
                    service_name=svc.name,
                    service_slug=svc.slug,
                    base_url=svc.base_url,
                    auth_type=svc.auth_type,
                    is_service_active=svc.is_active,
                    rate_limit_rpm=quota.rate_limit_rpm if quota else 60,
                    quota_daily=daily,
                    is_quota_active=quota.is_active if quota else True,
                    usage_today=usage,
                    usage_percentage=pct,
                    bound_at=quota.created_at if quota else svc.created_at,
                )
            )
        return results
