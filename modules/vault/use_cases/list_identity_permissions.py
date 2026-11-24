from modules.vault.domain.interfaces import IKeyPermissionRepository


class ListIdentityPermissionsUseCase:
    """Lists all permitted secret keys for an identity."""

    def __init__(self, permission_repo: IKeyPermissionRepository) -> None:
        self.permission_repo = permission_repo

    async def execute(
        self,
        project_id: str,
        identity_id: str,
    ) -> set[str]:
        return await self.permission_repo.get_permitted_keys_for_identity(
            project_id=project_id,
            identity_id=identity_id,
        )
