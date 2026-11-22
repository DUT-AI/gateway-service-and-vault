from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.vault.domain.entities import (
    KeyPermissionEntity,
    SecretItemEntity,
    SecretScopeEntity,
)
from modules.vault.domain.interfaces import ISecretRepository
from modules.vault.models.permission import KeyPermissionModel
from modules.vault.models.scope import SecretScopeModel
from modules.vault.models.secret import SecretHistoryModel, SecretItemModel


class SqlSecretRepository(ISecretRepository):
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

    def _permission_to_entity(self, model: KeyPermissionModel) -> KeyPermissionEntity:
        return KeyPermissionEntity(
            id=model.id,
            project_id=model.project_id,
            identity_id=model.identity_id,
            secret_key=model.secret_key,
            identity_type=model.identity_type,
            granted_by=model.granted_by,
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

    async def grant_key_permission(
        self,
        project_id: str,
        identity_id: str,
        secret_key: str,
        identity_type: str = "client",
        granted_by: str = "",
    ) -> KeyPermissionEntity:
        stmt = select(KeyPermissionModel).where(
            KeyPermissionModel.project_id == project_id,
            KeyPermissionModel.identity_id == identity_id,
            KeyPermissionModel.secret_key == secret_key,
        )
        res = await self.session.execute(stmt)
        model = res.scalar_one_or_none()

        if not model:
            model = KeyPermissionModel(
                project_id=project_id,
                identity_id=identity_id,
                identity_type=identity_type,
                secret_key=secret_key,
                granted_by=granted_by,
            )
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)

        return self._permission_to_entity(model)

    async def revoke_key_permission(
        self, project_id: str, identity_id: str, secret_key: str
    ) -> bool:
        stmt = delete(KeyPermissionModel).where(
            KeyPermissionModel.project_id == project_id,
            KeyPermissionModel.identity_id == identity_id,
            KeyPermissionModel.secret_key == secret_key,
        )
        res = await self.session.execute(stmt)
        return bool(res.rowcount and res.rowcount > 0)

    async def list_permissions_by_identity(
        self, project_id: str, identity_id: str
    ) -> list[str]:
        stmt = select(KeyPermissionModel.secret_key).where(
            KeyPermissionModel.project_id == project_id,
            KeyPermissionModel.identity_id == identity_id,
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_permitted_keys_for_identity(
        self, project_id: str, identity_id: str
    ) -> set[str]:
        keys = await self.list_permissions_by_identity(project_id, identity_id)
        return set(keys)
