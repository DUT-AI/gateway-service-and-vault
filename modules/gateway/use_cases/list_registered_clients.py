from modules.gateway.domain.entities import RegisteredClientEntity
from modules.gateway.domain.interfaces import IRegisteredClientRepository


class ListRegisteredClientsUseCase:
    """Use case to list registered client devices scoped by admin or owner_id."""

    def __init__(self, client_repo: IRegisteredClientRepository) -> None:
        self.client_repo = client_repo

    async def execute(
        self, owner_id: str | None = None, is_admin: bool = False
    ) -> list[RegisteredClientEntity]:
        if is_admin or owner_id is None:
            return await self.client_repo.list_all()
        return await self.client_repo.list_by_owner_id(owner_id)
