from modules.vault.domain.entities import KeyPermissionEntity
from modules.vault.domain.interfaces import IKeyPermissionRepository


class GrantKeyPermissionUseCase:
    """Grants an identity read permission for a secret key."""

    def __init__(self, permission_repo: IKeyPermissionRepository) -> None:
        self.permission_repo = permission_repo

    async def execute(
        self,
        project_id: str,
        identity_id: str,
        secret_key: str,
        identity_type: str = "client",
        granted_by: str = "admin",
    ) -> KeyPermissionEntity:
        return await self.permission_repo.grant_key_permission(
            project_id=project_id,
            identity_id=identity_id,
            secret_key=secret_key,
            identity_type=identity_type,
            granted_by=granted_by,
        )
