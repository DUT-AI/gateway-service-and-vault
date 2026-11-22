from modules.vault.domain.interfaces import ISecretRepository


class RevokeKeyPermissionUseCase:
    """Revokes an identity's read permission for a secret key."""

    def __init__(self, secret_repo: ISecretRepository) -> None:
        self.secret_repo = secret_repo

    async def execute(
        self,
        project_id: str,
        identity_id: str,
        secret_key: str,
    ) -> bool:
        return await self.secret_repo.revoke_key_permission(
            project_id=project_id,
            identity_id=identity_id,
            secret_key=secret_key,
        )
