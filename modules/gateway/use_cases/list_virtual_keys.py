from modules.gateway.domain.entities import VirtualAccessKeyEntity
from modules.gateway.domain.interfaces import (
    IRegisteredClientRepository,
    IVirtualAccessKeyRepository,
)


class ListVirtualKeysUseCase:
    """Use case to list virtual access keys for a given project, optionally filtered by client owner."""

    def __init__(
        self,
        key_repo: IVirtualAccessKeyRepository,
        client_repo: IRegisteredClientRepository,
    ) -> None:
        self.key_repo = key_repo
        self.client_repo = client_repo

    async def execute(
        self, project_id: str, owner_id_filter: str | None = None
    ) -> list[VirtualAccessKeyEntity]:
        keys = await self.key_repo.list_by_project(project_id)
        if owner_id_filter is None:
            return keys
        owned_clients = await self.client_repo.list_by_owner_id(owner_id_filter)
        owned_client_ids = {c.id for c in owned_clients}
        return [k for k in keys if k.client_id in owned_client_ids]
