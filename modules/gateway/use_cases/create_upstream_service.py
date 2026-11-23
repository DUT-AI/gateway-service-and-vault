import logging

from modules.gateway.client.apisix_client import ApisixAdminClient
from modules.gateway.domain.entities import UpstreamServiceEntity
from modules.gateway.domain.interfaces import IUpstreamServiceRepository

logger = logging.getLogger("apisix_sync")


class CreateUpstreamServiceUseCase:
    """Use case to register a new upstream service."""

    def __init__(
        self,
        service_repo: IUpstreamServiceRepository,
        apisix_client: ApisixAdminClient,
    ) -> None:
        self.service_repo = service_repo
        self.apisix_client = apisix_client

    async def execute(
        self,
        name: str,
        slug: str,
        base_url: str,
        auth_type: str,
        credential: str,
        timeout_seconds: int = 30,
    ) -> UpstreamServiceEntity:
        service = await self.service_repo.create(
            name=name,
            slug=slug,
            base_url=base_url,
            auth_type=auth_type,
            encrypted_credential=credential,
            timeout_seconds=timeout_seconds,
        )
        try:
            await self.apisix_client.sync_upstream_service_route(
                service_slug=slug,
                upstream_base_url=base_url,
                upstream_auth_type=auth_type,
                upstream_credential=credential,
            )
        except Exception as e:
            logger.warning("Could not sync upstream service to APISIX: %s", e)

        return service
