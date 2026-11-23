from modules.gateway.domain.entities import SecurityAlertEntity
from modules.gateway.domain.interfaces import IAuditEventRepository


class GetSecurityAlertsUseCase:
    """Retrieves synthesized real-time security anomalies."""

    def __init__(self, audit_repo: IAuditEventRepository) -> None:
        self.audit_repo = audit_repo

    async def execute(
        self,
        window_minutes: int = 5,
        threshold: int = 3,
    ) -> list[SecurityAlertEntity]:
        return await self.audit_repo.get_security_alerts(
            window_minutes=window_minutes,
            threshold=threshold,
        )
