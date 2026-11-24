from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.gateway.domain.entities import (
    QuotaPolicyEntity,
    UpstreamServiceEntity,
)
from modules.gateway.domain.interfaces import IQuotaPolicyRepository
from modules.gateway.models.project import project_upstream_association
from modules.gateway.models.quota import QuotaPolicyModel
from modules.gateway.models.service import UpstreamServiceModel


class SqlQuotaPolicyRepository(IQuotaPolicyRepository):
    """Repository managing project-upstream service bindings and quota policies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_allowed_services(
        self, project_id: str
    ) -> list[tuple[UpstreamServiceEntity, QuotaPolicyEntity | None]]:
        stmt = (
            select(UpstreamServiceModel, QuotaPolicyModel)
            .join(
                project_upstream_association,
                project_upstream_association.c.service_id == UpstreamServiceModel.id,
            )
            .outerjoin(
                QuotaPolicyModel,
                (QuotaPolicyModel.service_id == UpstreamServiceModel.id)
                & (QuotaPolicyModel.project_id == project_id)
                & (QuotaPolicyModel.client_id.is_(None)),
            )
            .where(project_upstream_association.c.project_id == project_id)
            .order_by(UpstreamServiceModel.name.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        items: list[tuple[UpstreamServiceEntity, QuotaPolicyEntity | None]] = []
        for service_model, quota_model in rows:
            service_entity = UpstreamServiceEntity(
                id=service_model.id,
                name=service_model.name,
                slug=service_model.slug,
                base_url=service_model.base_url,
                auth_type=service_model.auth_type,
                encrypted_credential=service_model.encrypted_credential,
                timeout_seconds=service_model.timeout_seconds,
                is_active=service_model.is_active,
                created_at=service_model.created_at,
                updated_at=service_model.updated_at,
            )
            quota_entity = None
            if quota_model:
                quota_entity = QuotaPolicyEntity(
                    id=quota_model.id,
                    project_id=quota_model.project_id,
                    service_id=quota_model.service_id,
                    client_id=quota_model.client_id,
                    rate_limit_rpm=quota_model.rate_limit_rpm,
                    quota_daily=quota_model.quota_daily,
                    is_active=quota_model.is_active,
                    created_at=quota_model.created_at,
                    updated_at=quota_model.updated_at,
                )
            items.append((service_entity, quota_entity))
        return items

    async def get_service_quota(
        self, project_id: str, service_id: str
    ) -> QuotaPolicyEntity | None:
        stmt = select(QuotaPolicyModel).where(
            (QuotaPolicyModel.project_id == project_id)
            & (QuotaPolicyModel.service_id == service_id)
            & (QuotaPolicyModel.is_active == True)
        )
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()
        if not model:
            return None
        return QuotaPolicyEntity(
            id=model.id,
            project_id=model.project_id,
            service_id=model.service_id,
            client_id=model.client_id,
            rate_limit_rpm=model.rate_limit_rpm,
            quota_daily=model.quota_daily,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def is_service_allowed(self, project_id: str, service_id: str) -> bool:
        stmt = select(project_upstream_association.c.project_id).where(
            (project_upstream_association.c.project_id == project_id)
            & (project_upstream_association.c.service_id == service_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def bind_service(
        self, project_id: str, service_id: str, rate_limit_rpm: int, quota_daily: int
    ) -> tuple[UpstreamServiceEntity, QuotaPolicyEntity]:
        stmt_svc = select(UpstreamServiceModel).where(
            UpstreamServiceModel.id == service_id
        )
        res_svc = await self.session.execute(stmt_svc)
        svc_model = res_svc.scalar_one_or_none()
        if not svc_model:
            raise ValueError(f"Upstream service '{service_id}' not found")

        if await self.is_service_allowed(project_id, service_id):
            raise ValueError(
                f"Service '{service_id}' is already bound to project '{project_id}'"
            )

        insert_stmt = project_upstream_association.insert().values(
            project_id=project_id, service_id=service_id
        )
        await self.session.execute(insert_stmt)

        stmt_q = select(QuotaPolicyModel).where(
            (QuotaPolicyModel.project_id == project_id)
            & (QuotaPolicyModel.service_id == service_id)
            & (QuotaPolicyModel.client_id.is_(None))
        )
        res_q = await self.session.execute(stmt_q)
        q_model = res_q.scalar_one_or_none()
        if q_model:
            q_model.rate_limit_rpm = rate_limit_rpm
            q_model.quota_daily = quota_daily
            q_model.is_active = True
        else:
            q_model = QuotaPolicyModel(
                project_id=project_id,
                service_id=service_id,
                client_id=None,
                rate_limit_rpm=rate_limit_rpm,
                quota_daily=quota_daily,
                is_active=True,
            )
            self.session.add(q_model)

        await self.session.flush()
        await self.session.refresh(q_model)

        svc_entity = UpstreamServiceEntity(
            id=svc_model.id,
            name=svc_model.name,
            slug=svc_model.slug,
            base_url=svc_model.base_url,
            auth_type=svc_model.auth_type,
            encrypted_credential=svc_model.encrypted_credential,
            timeout_seconds=svc_model.timeout_seconds,
            is_active=svc_model.is_active,
            created_at=svc_model.created_at,
            updated_at=svc_model.updated_at,
        )
        quota_entity = QuotaPolicyEntity(
            id=q_model.id,
            project_id=q_model.project_id,
            service_id=q_model.service_id,
            client_id=q_model.client_id,
            rate_limit_rpm=q_model.rate_limit_rpm,
            quota_daily=q_model.quota_daily,
            is_active=q_model.is_active,
            created_at=q_model.created_at,
            updated_at=q_model.updated_at,
        )
        return svc_entity, quota_entity

    async def unbind_service(self, project_id: str, service_id: str) -> bool:
        if not await self.is_service_allowed(project_id, service_id):
            return False

        del_assoc = project_upstream_association.delete().where(
            (project_upstream_association.c.project_id == project_id)
            & (project_upstream_association.c.service_id == service_id)
        )
        await self.session.execute(del_assoc)

        del_quota = delete(QuotaPolicyModel).where(
            (QuotaPolicyModel.project_id == project_id)
            & (QuotaPolicyModel.service_id == service_id)
        )
        await self.session.execute(del_quota)
        await self.session.flush()
        return True

    async def update_service_quota(
        self, project_id: str, service_id: str, rate_limit_rpm: int, quota_daily: int
    ) -> QuotaPolicyEntity:
        if not await self.is_service_allowed(project_id, service_id):
            raise ValueError(
                f"Service '{service_id}' is not bound to project '{project_id}'"
            )

        stmt_q = select(QuotaPolicyModel).where(
            (QuotaPolicyModel.project_id == project_id)
            & (QuotaPolicyModel.service_id == service_id)
            & (QuotaPolicyModel.client_id.is_(None))
        )
        res_q = await self.session.execute(stmt_q)
        q_model = res_q.scalar_one_or_none()
        if not q_model:
            q_model = QuotaPolicyModel(
                project_id=project_id,
                service_id=service_id,
                client_id=None,
                rate_limit_rpm=rate_limit_rpm,
                quota_daily=quota_daily,
                is_active=True,
            )
            self.session.add(q_model)
        else:
            q_model.rate_limit_rpm = rate_limit_rpm
            q_model.quota_daily = quota_daily
            q_model.is_active = True

        await self.session.flush()
        await self.session.refresh(q_model)
        return QuotaPolicyEntity(
            id=q_model.id,
            project_id=q_model.project_id,
            service_id=q_model.service_id,
            client_id=q_model.client_id,
            rate_limit_rpm=q_model.rate_limit_rpm,
            quota_daily=q_model.quota_daily,
            is_active=q_model.is_active,
            created_at=q_model.created_at,
            updated_at=q_model.updated_at,
        )
