from core.config import auth_settings
from core.exceptions import UnauthorizedError
from core.security.jwt import create_access_token
from core.security.password import verify_password
from modules.identity.domain.exceptions import InvalidCredentialsError
from modules.identity.domain.interfaces import IUserRepository
from modules.identity.dtos.auth_dtos import TokenResponse, UserLoginRequest


class LoginUserUseCase:
    """Use case for authenticating users and issuing tokens."""

    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    async def execute(self, req: UserLoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(req.email)
        if not user or not user.password_hash:
            raise InvalidCredentialsError()

        if not verify_password(req.password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.is_active():
            raise UnauthorizedError("User account is inactive or disabled")

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
            }
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_settings.access_token_expire_minutes * 60,
        )
