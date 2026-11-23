from modules.gateway.domain.interfaces import IRegisteredClientRepository
from modules.gateway.use_cases.exceptions import ClientNotFoundError


class RevokeClientUseCase:
    """Use case to revoke a registered client device and all its active virtual keys."""

    def __init__(self, client_repo: IRegisteredClientRepository) -> None:
        self.client_repo = client_repo

    async def execute(self, client_id: str) -> bool:
        client = await self.client_repo.get_by_id(client_id)
        if not client:
            raise ClientNotFoundError(f"Client '{client_id}' not found")

        if client.is_revoked:
            return True

        return await self.client_repo.revoke_client(client_id)
