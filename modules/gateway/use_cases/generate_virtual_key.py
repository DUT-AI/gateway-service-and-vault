import secrets

from core.security.ca import PrivateCA
from modules.gateway.domain.entities import VirtualAccessKeyEntity
from modules.gateway.domain.interfaces import (
    IProjectRepository,
    IRegisteredClientRepository,
    IVirtualAccessKeyRepository,
)
from modules.gateway.use_cases.exceptions import (
    ClientNotFoundError,
    ProjectNotFoundError,
)


class GenerateVirtualKeyUseCase:
    """Generates a Virtual Access Key bound to a registered client and project."""

    def __init__(
        self,
        client_repo: IRegisteredClientRepository,
        project_repo: IProjectRepository,
        key_repo: IVirtualAccessKeyRepository,
    ) -> None:
        self.client_repo = client_repo
        self.project_repo = project_repo
        self.key_repo = key_repo

    async def execute(
        self,
        client_id: str,
        project_id: str,
    ) -> tuple[VirtualAccessKeyEntity, str]:
        client = await self.client_repo.get_by_id(client_id)
        if not client:
            raise ClientNotFoundError(f"Client {client_id} not found")

        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        # Generate random high-entropy token: vk_live_<32_bytes_hex>
        raw_token = f"vk_live_{secrets.token_hex(20)}"
        key_prefix = raw_token[:12]
        key_hash = PrivateCA.hash_virtual_key(raw_token)

        key_entity = await self.key_repo.create(
            key_hash=key_hash,
            key_prefix=key_prefix,
            client_id=client_id,
            project_id=project_id,
        )
        return key_entity, raw_token
