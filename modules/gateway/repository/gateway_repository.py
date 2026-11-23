from datetime import UTC, datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.gateway.domain.entities import (
    ClientType,
    KeyStatus,
    ProjectEntity,
    QuotaPolicyEntity,
    RegisteredClientEntity,
    UpstreamServiceEntity,
    VirtualAccessKeyEntity,
)
from modules.gateway.domain.interfaces import (
    IProjectRepository,
    IRegisteredClientRepository,
    IUpstreamServiceRepository,
    IVirtualAccessKeyRepository,
)
from modules.gateway.models.client import RegisteredClientModel
from modules.gateway.models.project import ProjectModel, project_upstream_association
from modules.gateway.models.quota import QuotaPolicyModel
from modules.gateway.models.service import UpstreamServiceModel
from modules.gateway.models.virtual_key import VirtualAccessKeyModel
from modules.gateway.use_cases.exceptions import (
    ProjectNotFoundError,
    ServiceAlreadyBoundError,
    ServiceNotBoundError,
    ServiceNotFoundError,
)


class SqlProjectRepository(IProjectRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: ProjectModel) -> ProjectEntity:
        return ProjectEntity(
            id=model.id,
            name=model.name,
            slug=model.slug,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, project_id: str) -> ProjectEntity | None:
        stmt = select(ProjectModel).where(ProjectModel.id == project_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> ProjectEntity | None:
        stmt = select(ProjectModel).where(ProjectModel.slug == slug)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(
        self, name: str, slug: str, description: str | None = None
    ) -> ProjectEntity:
        model = ProjectModel(name=name, slug=slug, description=description)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def list_all(self) -> list[ProjectEntity]:
        stmt = select(ProjectModel).order_by(ProjectModel.created_at.desc())
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

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
        project = await self.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project '{project_id}' not found")

        stmt_svc = select(UpstreamServiceModel).where(
            UpstreamServiceModel.id == service_id
        )
        res_svc = await self.session.execute(stmt_svc)
        svc_model = res_svc.scalar_one_or_none()
        if not svc_model:
            raise ServiceNotFoundError(f"Upstream service '{service_id}' not found")

        if await self.is_service_allowed(project_id, service_id):
            raise ServiceAlreadyBoundError(
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
            raise ServiceNotBoundError(
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


class SqlRegisteredClientRepository(IRegisteredClientRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: RegisteredClientModel) -> RegisteredClientEntity:
        return RegisteredClientEntity(
            id=model.id,
            client_type=ClientType(model.client_type),
            name=model.name,
            owner_id=model.owner_id,
            cert_fingerprint=model.cert_fingerprint,
            cert_serial=model.cert_serial,
            expires_at=model.expires_at,
            is_revoked=model.is_revoked,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, client_id: str) -> RegisteredClientEntity | None:
        stmt = select(RegisteredClientModel).where(
            RegisteredClientModel.id == client_id
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_cert_fingerprint(
        self, cert_fingerprint: str
    ) -> RegisteredClientEntity | None:
        stmt = select(RegisteredClientModel).where(
            RegisteredClientModel.cert_fingerprint == cert_fingerprint
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(
        self,
        name: str,
        client_type: ClientType,
        owner_id: str,
        cert_fingerprint: str,
        cert_serial: str,
        expires_at: datetime,
    ) -> RegisteredClientEntity:
        model = RegisteredClientModel(
            name=name,
            client_type=client_type.value,
            owner_id=owner_id,
            cert_fingerprint=cert_fingerprint,
            cert_serial=cert_serial,
            expires_at=expires_at,
            is_revoked=False,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def list_all(self) -> list[RegisteredClientEntity]:
        stmt = select(RegisteredClientModel).order_by(
            RegisteredClientModel.created_at.desc()
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]


class SqlVirtualAccessKeyRepository(IVirtualAccessKeyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: VirtualAccessKeyModel) -> VirtualAccessKeyEntity:
        return VirtualAccessKeyEntity(
            id=model.id,
            key_hash=model.key_hash,
            key_prefix=model.key_prefix,
            client_id=model.client_id,
            project_id=model.project_id,
            status=KeyStatus(model.status),
            last_used_at=model.last_used_at,
            created_at=model.created_at,
            revoked_at=model.revoked_at,
        )

    async def get_by_key_hash(self, key_hash: str) -> VirtualAccessKeyEntity | None:
        stmt = select(VirtualAccessKeyModel).where(
            VirtualAccessKeyModel.key_hash == key_hash
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_active_by_client_and_project(
        self, client_id: str, project_id: str
    ) -> VirtualAccessKeyEntity | None:
        stmt = select(VirtualAccessKeyModel).where(
            VirtualAccessKeyModel.client_id == client_id,
            VirtualAccessKeyModel.project_id == project_id,
            VirtualAccessKeyModel.status == KeyStatus.ACTIVE.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def revoke_active_keys(self, client_id: str, project_id: str) -> int:
        now = datetime.now(UTC)
        stmt = (
            update(VirtualAccessKeyModel)
            .where(
                VirtualAccessKeyModel.client_id == client_id,
                VirtualAccessKeyModel.project_id == project_id,
                VirtualAccessKeyModel.status == KeyStatus.ACTIVE.value,
            )
            .values(status=KeyStatus.REVOKED.value, revoked_at=now)
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def create(
        self,
        key_hash: str,
        key_prefix: str,
        client_id: str,
        project_id: str,
    ) -> VirtualAccessKeyEntity:
        # Enforce single active key policy
        await self.revoke_active_keys(client_id, project_id)

        model = VirtualAccessKeyModel(
            key_hash=key_hash,
            key_prefix=key_prefix,
            client_id=client_id,
            project_id=project_id,
            status=KeyStatus.ACTIVE.value,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def list_by_project(self, project_id: str) -> list[VirtualAccessKeyEntity]:
        stmt = (
            select(VirtualAccessKeyModel)
            .where(VirtualAccessKeyModel.project_id == project_id)
            .order_by(VirtualAccessKeyModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def revoke_by_id(self, key_id: str) -> bool:
        now = datetime.now(UTC)
        stmt = (
            update(VirtualAccessKeyModel)
            .where(VirtualAccessKeyModel.id == key_id)
            .values(status=KeyStatus.REVOKED.value, revoked_at=now)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0


class SqlUpstreamServiceRepository(IUpstreamServiceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: UpstreamServiceModel) -> UpstreamServiceEntity:
        return UpstreamServiceEntity(
            id=model.id,
            name=model.name,
            slug=model.slug,
            base_url=model.base_url,
            auth_type=model.auth_type,
            encrypted_credential=model.encrypted_credential,
            timeout_seconds=model.timeout_seconds,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def list_all(self) -> list[UpstreamServiceEntity]:
        stmt = select(UpstreamServiceModel).order_by(
            UpstreamServiceModel.created_at.desc()
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_id(self, service_id: str) -> UpstreamServiceEntity | None:
        stmt = select(UpstreamServiceModel).where(UpstreamServiceModel.id == service_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(
        self,
        name: str,
        slug: str,
        base_url: str,
        auth_type: str,
        encrypted_credential: str,
        timeout_seconds: int = 30,
    ) -> UpstreamServiceEntity:
        model = UpstreamServiceModel(
            name=name,
            slug=slug,
            base_url=base_url,
            auth_type=auth_type,
            encrypted_credential=encrypted_credential,
            timeout_seconds=timeout_seconds,
            is_active=True,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)
