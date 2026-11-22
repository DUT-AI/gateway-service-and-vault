from modules.gateway.domain.entities import RegisteredClientEntity
from modules.gateway.domain.interfaces import IRegisteredClientRepository


class ListRegisteredClientsUseCase:
    """Use case to list all registered client devices and machine identities."""

    def __init__(self, client_repo: IRegisteredClientRepository) -> None:
        self.client_repo = client_repo

    async def execute(self) -> list[RegisteredClientEntity]:
        return await self.client_repo.list_all()
