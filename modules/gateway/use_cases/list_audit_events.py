from datetime import datetime

from modules.gateway.domain.entities import AuditEventEntity
from modules.gateway.domain.interfaces import IAuditEventRepository


class ListAuditEventsUseCase:
    """Retrieves filtered, paginated audit log records."""

    def __init__(self, audit_repo: IAuditEventRepository) -> None:
        self.audit_repo = audit_repo

    async def execute(
        self,
        project_id: str | None = None,
        client_type: str | None = None,
        decision: str | None = None,
        action: str | None = None,
        error_code: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AuditEventEntity], int]:
        return await self.audit_repo.list_events(
            project_id=project_id,
            client_type=client_type,
            decision=decision,
            action=action,
            error_code=error_code,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
