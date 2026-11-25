from datetime import datetime
from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Query

from apps.api.routers.gateway.access_helpers import ensure_project_access
from core.security.deps import require_role_tier
from core.security.roles import RoleTier, UserContext
from modules.gateway.dtos.audit_dtos import (
    AuditEventListResponse,
    AuditEventResponse,
    SecurityAlertItemResponse,
    SecurityAlertsResponse,
)
from modules.gateway.use_cases import (
    CheckProjectMembershipUseCase,
    GetSecurityAlertsUseCase,
    ListAuditEventsUseCase,
)

router = APIRouter()


@router.get(
    "/audit-events",
    response_model=AuditEventListResponse,
    summary="Query audit log records with filters and pagination",
)
@inject
async def list_audit_events(
    use_case: FromDishka[ListAuditEventsUseCase],
    membership_uc: FromDishka[CheckProjectMembershipUseCase],
    user_ctx: Annotated[
        UserContext,
        Depends(require_role_tier(RoleTier.ADMIN, RoleTier.PROJECT_DEVELOPER)),
    ],
    project_id: str | None = None,
    client_type: str | None = None,
    decision: str | None = None,
    action: str | None = None,
    error_code: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AuditEventListResponse:
    """Query immutable security audit logs with filtering and pagination."""
    if project_id:
        await ensure_project_access(project_id, user_ctx, membership_uc)
    events, total = await use_case.execute(
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
    return AuditEventListResponse(
        items=[
            AuditEventResponse(
                id=e.id,
                timestamp=e.timestamp,
                client_type=(
                    e.client_type.value
                    if hasattr(e.client_type, "value")
                    else str(e.client_type)
                ),
                actor_id=e.actor_id,
                project_id=e.project_id,
                service_id=e.service_id,
                action=e.action,
                decision=e.decision,
                client_ip=e.client_ip,
                error_code=e.error_code,
                metadata=e.metadata,
            )
            for e in events
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/security-alerts",
    response_model=SecurityAlertsResponse,
    summary="Retrieve active security anomaly alerts",
)
@inject
async def get_security_alerts(
    use_case: FromDishka[GetSecurityAlertsUseCase],
    _: Annotated[
        UserContext,
        Depends(require_role_tier(RoleTier.ADMIN, RoleTier.PROJECT_DEVELOPER)),
    ],
    window_minutes: int = Query(default=5, ge=1, le=60),
    threshold: int = Query(default=3, ge=1, le=100),
) -> SecurityAlertsResponse:
    """Retrieve active security anomalies such as repeated Identity Mismatch violations."""
    alerts = await use_case.execute(
        window_minutes=window_minutes,
        threshold=threshold,
    )
    items = [
        SecurityAlertItemResponse(
            alert_id=a.alert_id,
            severity=a.severity,
            anomaly_type=a.anomaly_type,
            description=a.description,
            actor_id=a.actor_id,
            client_ip=a.client_ip,
            event_count=a.event_count,
            first_seen_at=a.first_seen_at,
            last_seen_at=a.last_seen_at,
        )
        for a in alerts
    ]
    return SecurityAlertsResponse(
        alerts=items,
        total_active=len(items),
    )
