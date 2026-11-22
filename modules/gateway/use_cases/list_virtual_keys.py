from modules.gateway.domain.entities import VirtualAccessKeyEntity
from modules.gateway.domain.interfaces import IVirtualAccessKeyRepository


class ListVirtualKeysUseCase:
    """Use case to list all virtual access keys for a given project."""

    def __init__(self, key_repo: IVirtualAccessKeyRepository) -> None:
        self.key_repo = key_repo

    async def execute(self, project_id: str) -> list[VirtualAccessKeyEntity]:
        return await self.key_repo.list_by_project(project_id)
