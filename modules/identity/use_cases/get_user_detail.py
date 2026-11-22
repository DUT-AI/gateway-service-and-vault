from core.exceptions.base import EntityNotFoundError
from modules.identity.domain.entities import ExternalUserDetailEntity
from modules.identity.domain.interfaces import IExternalUserDirectoryService


class UserNotFoundError(EntityNotFoundError):
    def __init__(self, message: str = "User not found in central directory") -> None:
        super().__init__(message=message)


class GetUserDetailUseCase:
    """Retrieves detailed user profile by integer ID from the central directory."""

    def __init__(self, directory_service: IExternalUserDirectoryService) -> None:
        self.directory_service = directory_service

    async def execute(
        self, user_id: int, auth_token: str | None = None
    ) -> ExternalUserDetailEntity:
        user = await self.directory_service.get_user_by_id(
            user_id=user_id, auth_token=auth_token
        )
        if not user:
            raise UserNotFoundError(
                f"User with ID {user_id} not found in central directory"
            )
        return user
