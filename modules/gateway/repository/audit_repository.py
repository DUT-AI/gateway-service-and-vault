from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.gateway.domain.entities import (
    AuditEventEntity,
    ClientType,
    SecurityAlertEntity,
)
from modules.gateway.domain.interfaces import IAuditEventRepository
from modules.gateway.models.audit import AuditEventModel


class SqlAuditEventRepository(IAuditEventRepository):
    """SQLAlchemy implementation of IAuditEventRepository for PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: AuditEventModel) -> AuditEventEntity:
        # Map string client_type back to ClientType enum if valid
        try:
            client_type = ClientType(model.client_type)
        except ValueError:
            client_type = ClientType.USER_DEVICE

        return AuditEventEntity(
            id=model.id,
            timestamp=model.timestamp,
            client_type=client_type,
            actor_id=model.actor_id,
            project_id=model.project_id,
            service_id=model.service_id,
            action=model.action,
            decision=model.decision,
            client_ip=model.client_ip,
            error_code=model.error_code,
            metadata=model.metadata_json or {},
        )

    async def record_event(
        self,
        event: AuditEventEntity,
    ) -> AuditEventEntity:
        client_type_str = (
            event.client_type.value
            if isinstance(event.client_type, ClientType)
            else str(event.client_type)
        )

        model = AuditEventModel(
            id=event.id,
            timestamp=event.timestamp,
            client_type=client_type_str,
            actor_id=event.actor_id,
            project_id=event.project_id,
            service_id=event.service_id,
            action=event.action,
            decision=event.decision,
            client_ip=event.client_ip,
            error_code=event.error_code,
            metadata_json=event.metadata or {},
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def list_events(
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
        stmt = select(AuditEventModel)
        count_stmt = select(func.count()).select_from(AuditEventModel)

        filters = []
        if project_id:
            filters.append(AuditEventModel.project_id == project_id)
        if client_type:
            filters.append(AuditEventModel.client_type == client_type)
        if decision:
            filters.append(AuditEventModel.decision == decision)
        if action:
            filters.append(AuditEventModel.action == action)
        if error_code:
            filters.append(AuditEventModel.error_code == error_code)
        if date_from:
            filters.append(AuditEventModel.timestamp >= date_from)
        if date_to:
            filters.append(AuditEventModel.timestamp <= date_to)

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        # Count total
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one() or 0

        # Fetch page ordered by timestamp descending
        stmt = (
            stmt.order_by(AuditEventModel.timestamp.desc()).offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(m) for m in models], total

    async def get_security_alerts(
        self,
        window_minutes: int = 5,
        threshold: int = 3,
    ) -> list[SecurityAlertEntity]:
        window_start = datetime.now(UTC) - timedelta(minutes=window_minutes)

        stmt = (
            select(
                AuditEventModel.actor_id,
                AuditEventModel.client_ip,
                func.count().label("event_count"),
                func.min(AuditEventModel.timestamp).label("first_seen_at"),
                func.max(AuditEventModel.timestamp).label("last_seen_at"),
            )
            .where(
                AuditEventModel.action == "GATEWAY_ACCESS",
                AuditEventModel.error_code == "IDENTITY_MISMATCH",
                AuditEventModel.timestamp >= window_start,
            )
            .group_by(AuditEventModel.actor_id, AuditEventModel.client_ip)
            .having(func.count() >= threshold)
            .order_by(func.count().desc())
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        alerts: list[SecurityAlertEntity] = []
        for row in rows:
            actor = row.actor_id
            ip = row.client_ip
            count = row.event_count
            first_seen = row.first_seen_at
            last_seen = row.last_seen_at

            alert_id = f"alert_imm_{actor}_{int(last_seen.timestamp())}"
            desc = (
                f"Client {actor} (IP: {ip or 'unknown'}) triggered "
                f"{count} Identity Mismatch violations within {window_minutes} minutes."
            )
            alerts.append(
                SecurityAlertEntity(
                    alert_id=alert_id,
                    severity="HIGH",
                    anomaly_type="REPEATED_IDENTITY_MISMATCH",
                    description=desc,
                    actor_id=actor,
                    client_ip=ip,
                    event_count=count,
                    first_seen_at=first_seen,
                    last_seen_at=last_seen,
                )
            )

        return alerts
