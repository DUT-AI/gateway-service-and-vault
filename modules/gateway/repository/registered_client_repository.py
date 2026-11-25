from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.gateway.domain.entities import (
    ClientType,
    RegisteredClientEntity,
)
from modules.gateway.domain.interfaces import IRegisteredClientRepository
from modules.gateway.models.client import RegisteredClientModel


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

    async def list_by_owner_id(self, owner_id: str) -> list[RegisteredClientEntity]:
        stmt = (
            select(RegisteredClientModel)
            .where(RegisteredClientModel.owner_id == owner_id)
            .order_by(RegisteredClientModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def list_by_owner_ids(
        self, owner_ids: list[str]
    ) -> list[RegisteredClientEntity]:
        if not owner_ids:
            return []
        stmt = (
            select(RegisteredClientModel)
            .where(RegisteredClientModel.owner_id.in_(owner_ids))
            .order_by(RegisteredClientModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def revoke_client(self, client_id: str) -> bool:
        stmt_client = (
            update(RegisteredClientModel)
            .where(RegisteredClientModel.id == client_id)
            .values(is_revoked=True)
        )
        res = await self.session.execute(stmt_client)
        await self.session.flush()
        return res.rowcount > 0
