from modules.vault.domain.entities import KeyPermissionEntity
from modules.vault.domain.interfaces import ISecretRepository


class GrantKeyPermissionUseCase:
    """Grants an identity read permission for a secret key."""

    def __init__(self, secret_repo: ISecretRepository) -> None:
        self.secret_repo = secret_repo

    async def execute(
        self,
        project_id: str,
        identity_id: str,
        secret_key: str,
        identity_type: str = "client",
        granted_by: str = "admin",
    ) -> KeyPermissionEntity:
        return await self.secret_repo.grant_key_permission(
            project_id=project_id,
            identity_id=identity_id,
            secret_key=secret_key,
            identity_type=identity_type,
            granted_by=granted_by,
        )
