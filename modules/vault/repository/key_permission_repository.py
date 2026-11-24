from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.vault.domain.entities import KeyPermissionEntity
from modules.vault.domain.interfaces import IKeyPermissionRepository
from modules.vault.models.permission import KeyPermissionModel


class SqlKeyPermissionRepository(IKeyPermissionRepository):
    """Repository strictly responsible for KeyPermission aggregate root persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

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
        await self.session.flush()
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
