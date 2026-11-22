from modules.identity.domain.entities import ExternalUserOptionEntity
from modules.identity.domain.interfaces import IExternalUserDirectoryService


class GetUserOptionsUseCase:
    """Retrieves all user options from the central DUT-AI directory."""

    def __init__(self, directory_service: IExternalUserDirectoryService) -> None:
        self.directory_service = directory_service

    async def execute(
        self, auth_token: str | None = None
    ) -> list[ExternalUserOptionEntity]:
        return await self.directory_service.get_user_options(auth_token=auth_token)
