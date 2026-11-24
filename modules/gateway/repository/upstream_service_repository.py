from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.gateway.domain.entities import UpstreamServiceEntity
from modules.gateway.domain.interfaces import IUpstreamServiceRepository
from modules.gateway.models.service import UpstreamServiceModel


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

    async def get_by_slug(self, slug: str) -> UpstreamServiceEntity | None:
        stmt = select(UpstreamServiceModel).where(UpstreamServiceModel.slug == slug)
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
