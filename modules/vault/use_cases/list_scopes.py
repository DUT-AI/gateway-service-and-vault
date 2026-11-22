from modules.vault.domain.entities import SecretScopeEntity
from modules.vault.domain.interfaces import ISecretRepository


class ListScopesUseCase:
    """Use case to list all secret scopes defined in a project."""

    def __init__(self, secret_repo: ISecretRepository) -> None:
        self.secret_repo = secret_repo

    async def execute(self, project_id: str) -> list[SecretScopeEntity]:
        return await self.secret_repo.list_scopes(project_id)
