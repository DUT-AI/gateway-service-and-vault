from core.utils.datetime_utils import now_utc
from modules.identity.domain.exceptions import UserNotFoundError
from modules.identity.domain.interfaces import IUserRepository
from modules.identity.dtos.auth_dtos import UserResponse


class GetCurrentUserUseCase:
    """Use case for retrieving current authenticated user profile."""

    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    async def execute(self, user_id: int) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        roles = [user.role] if user.role else ["member"]
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            avatar_url=user.avatar_url,
            status=user.status,
            role_names=roles,
            permissions=["*"] if user.role == "admin" else [],
            created_at=user.created_at or now_utc(),
        )
