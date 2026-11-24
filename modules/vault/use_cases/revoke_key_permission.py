from modules.vault.domain.interfaces import IKeyPermissionRepository


class RevokeKeyPermissionUseCase:
    """Revokes an identity's read permission for a secret key."""

    def __init__(self, permission_repo: IKeyPermissionRepository) -> None:
        self.permission_repo = permission_repo

    async def execute(
        self,
        project_id: str,
        identity_id: str,
        secret_key: str,
    ) -> bool:
        return await self.permission_repo.revoke_key_permission(
            project_id=project_id,
            identity_id=identity_id,
            secret_key=secret_key,
        )
