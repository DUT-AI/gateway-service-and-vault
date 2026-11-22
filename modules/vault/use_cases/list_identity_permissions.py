from modules.vault.domain.interfaces import ISecretRepository


class ListIdentityPermissionsUseCase:
    """Lists all permitted secret keys for an identity."""

    def __init__(self, secret_repo: ISecretRepository) -> None:
        self.secret_repo = secret_repo

    async def execute(
        self,
        project_id: str,
        identity_id: str,
    ) -> set[str]:
        return await self.secret_repo.get_permitted_keys_for_identity(
            project_id=project_id,
            identity_id=identity_id,
        )
