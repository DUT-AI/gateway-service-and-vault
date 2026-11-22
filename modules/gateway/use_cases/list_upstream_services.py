from modules.gateway.domain.entities import UpstreamServiceEntity
from modules.gateway.domain.interfaces import IUpstreamServiceRepository


class ListUpstreamServicesUseCase:
    """Use case to list all upstream backend services."""

    def __init__(self, service_repo: IUpstreamServiceRepository) -> None:
        self.service_repo = service_repo

    async def execute(self) -> list[UpstreamServiceEntity]:
        return await self.service_repo.list_all()
