from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.gateway.domain.entities import KeyStatus, VirtualAccessKeyEntity
from modules.gateway.domain.interfaces import IVirtualAccessKeyRepository
from modules.gateway.models.virtual_key import VirtualAccessKeyModel


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
        await self.session.flush()
        return result.rowcount

    async def revoke_all_by_client(self, client_id: str) -> int:
        now = datetime.now(UTC)
        stmt = (
            update(VirtualAccessKeyModel)
            .where(
                VirtualAccessKeyModel.client_id == client_id,
                VirtualAccessKeyModel.status == KeyStatus.ACTIVE.value,
            )
            .values(status=KeyStatus.REVOKED.value, revoked_at=now)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    async def create(
        self,
        key_hash: str,
        key_prefix: str,
        client_id: str,
        project_id: str,
    ) -> VirtualAccessKeyEntity:
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
        await self.session.flush()
        return result.rowcount > 0
