from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.vault.domain.entities import (
    SecretItemEntity,
    SecretScopeEntity,
)
from modules.vault.domain.interfaces import ISecretRepository
from modules.vault.models.scope import SecretScopeModel
from modules.vault.models.secret import SecretHistoryModel, SecretItemModel


class SqlSecretRepository(ISecretRepository):
    """Repository strictly responsible for SecretScope and SecretItem persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _scope_to_entity(self, model: SecretScopeModel) -> SecretScopeEntity:
        return SecretScopeEntity(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _secret_to_entity(self, model: SecretItemModel) -> SecretItemEntity:
        return SecretItemEntity(
            id=model.id,
            project_id=model.project_id,
            scope_id=model.scope_id,
            key=model.key,
            encrypted_value=model.encrypted_value,
            nonce=model.nonce,
            auth_tag=model.auth_tag,
            version=model.version,
            created_by=model.created_by,
            updated_by=model.updated_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_or_create_scope(
        self, project_id: str, scope_name: str, description: str | None = None
    ) -> SecretScopeEntity:
        stmt = select(SecretScopeModel).where(
            SecretScopeModel.project_id == project_id,
            SecretScopeModel.name == scope_name,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            model = SecretScopeModel(
                project_id=project_id,
                name=scope_name,
                description=description,
            )
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)

        return self._scope_to_entity(model)

    async def list_scopes(self, project_id: str) -> list[SecretScopeEntity]:
        stmt = select(SecretScopeModel).where(SecretScopeModel.project_id == project_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._scope_to_entity(m) for m in models]

    async def get_secrets_by_scope(
        self, project_id: str, scope_name: str
    ) -> list[SecretItemEntity]:
        stmt = (
            select(SecretItemModel)
            .join(SecretScopeModel, SecretItemModel.scope_id == SecretScopeModel.id)
            .where(
                SecretItemModel.project_id == project_id,
                SecretScopeModel.name == scope_name,
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._secret_to_entity(m) for m in models]

    async def upsert_secret(
        self,
        project_id: str,
        scope_name: str,
        key: str,
        encrypted_value: str,
        nonce: str,
        auth_tag: str,
        actor: str = "",
    ) -> SecretItemEntity:
        scope = await self.get_or_create_scope(project_id, scope_name)

        stmt = select(SecretItemModel).where(
            SecretItemModel.project_id == project_id,
            SecretItemModel.scope_id == scope.id,
            SecretItemModel.key == key,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            # Archive previous version to history
            history = SecretHistoryModel(
                secret_id=model.id,
                version=model.version,
                encrypted_value=model.encrypted_value,
                nonce=model.nonce,
                auth_tag=model.auth_tag,
                modified_by=model.updated_by or actor,
            )
            self.session.add(history)

            model.encrypted_value = encrypted_value
            model.nonce = nonce
            model.auth_tag = auth_tag
            model.version += 1
            model.updated_by = actor
        else:
            model = SecretItemModel(
                project_id=project_id,
                scope_id=scope.id,
                key=key,
                encrypted_value=encrypted_value,
                nonce=nonce,
                auth_tag=auth_tag,
                version=1,
                created_by=actor,
                updated_by=actor,
            )
            self.session.add(model)

        await self.session.flush()
        await self.session.refresh(model)
        return self._secret_to_entity(model)

    async def delete_secret(self, project_id: str, scope_name: str, key: str) -> bool:
        stmt = (
            select(SecretItemModel)
            .join(SecretScopeModel, SecretItemModel.scope_id == SecretScopeModel.id)
            .where(
                SecretItemModel.project_id == project_id,
                SecretScopeModel.name == scope_name,
                SecretItemModel.key == key,
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False

        await self.session.delete(model)
        await self.session.flush()
        return True
