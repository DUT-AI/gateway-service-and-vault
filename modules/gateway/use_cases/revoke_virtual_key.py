from modules.gateway.domain.interfaces import IVirtualAccessKeyRepository


class RevokeVirtualKeyUseCase:
    """Use case to revoke a virtual access key by its ID."""

    def __init__(self, key_repo: IVirtualAccessKeyRepository) -> None:
        self.key_repo = key_repo

    async def execute(self, key_id: str) -> bool:
        return await self.key_repo.revoke_by_id(key_id)
