from modules.gateway.domain.entities import UpstreamServiceEntity
from modules.gateway.domain.interfaces import IUpstreamServiceRepository


class CreateUpstreamServiceUseCase:
    """Use case to register a new upstream service."""

    def __init__(self, service_repo: IUpstreamServiceRepository) -> None:
        self.service_repo = service_repo

    async def execute(
        self,
        name: str,
        slug: str,
        base_url: str,
        auth_type: str,
        credential: str,
        timeout_seconds: int = 30,
    ) -> UpstreamServiceEntity:
        return await self.service_repo.create(
            name=name,
            slug=slug,
            base_url=base_url,
            auth_type=auth_type,
            encrypted_credential=credential,
            timeout_seconds=timeout_seconds,
        )
