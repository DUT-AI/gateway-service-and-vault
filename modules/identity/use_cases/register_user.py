from core.security.password import hash_password
from core.utils.datetime_utils import now_utc
from modules.identity.domain.exceptions import UserAlreadyExistsError
from modules.identity.domain.interfaces import IUserRepository
from modules.identity.dtos.auth_dtos import UserRegisterRequest, UserResponse


class RegisterUserUseCase:
    """Use case to handle new user registration."""

    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    async def execute(self, req: UserRegisterRequest) -> UserResponse:
        existing = await self.user_repo.get_by_email(req.email)
        if existing:
            raise UserAlreadyExistsError(req.email)

        pwd_hash = hash_password(req.password)
        user = await self.user_repo.create(
            email=req.email,
            password_hash=pwd_hash,
            name=req.name,
        )

        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            avatar_url=user.avatar_url,
            status=user.status,
            created_at=user.created_at or now_utc(),
        )
