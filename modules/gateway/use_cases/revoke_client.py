from modules.gateway.domain.interfaces import (
    IRegisteredClientRepository,
    IVirtualAccessKeyRepository,
)
from modules.gateway.use_cases.exceptions import (
    ClientNotFoundError,
    ClientOwnershipDeniedError,
)


class RevokeClientUseCase:
    """Use case to revoke a registered client device and all its active virtual keys."""

    def __init__(
        self,
        client_repo: IRegisteredClientRepository,
        key_repo: IVirtualAccessKeyRepository,
    ) -> None:
        self.client_repo = client_repo
        self.key_repo = key_repo

    async def execute(
        self,
        client_id: str,
        caller_owner_id: str | None = None,
        is_admin: bool = False,
    ) -> bool:
        client = await self.client_repo.get_by_id(client_id)
        if not client:
            raise ClientNotFoundError(f"Client '{client_id}' not found")

        if (
            not is_admin
            and caller_owner_id is not None
            and client.owner_id != caller_owner_id
        ):
            raise ClientOwnershipDeniedError(
                "Bạn không có quyền thu hồi thiết bị của người dùng khác"
            )

        if client.is_revoked:
            return True

        revoked = await self.client_repo.revoke_client(client_id)
        if revoked:
            await self.key_repo.revoke_all_by_client(client_id)
        return revoked
