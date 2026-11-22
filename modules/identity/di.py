from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.identity.domain.interfaces import IUserRepository
from modules.identity.repository.user_repository import SqlUserRepository
from modules.identity.use_cases import (
    GetCurrentUserUseCase,
    ListUsersUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
)


class IdentityProvider(Provider):
    """Dishka DI Provider for Identity feature module."""

    scope = Scope.REQUEST

    @provide
    def get_user_repository(self, session: AsyncSession) -> IUserRepository:
        return SqlUserRepository(session)

    register_user_uc = provide(RegisterUserUseCase)
    login_user_uc = provide(LoginUserUseCase)
    get_current_user_uc = provide(GetCurrentUserUseCase)
    list_users_uc = provide(ListUsersUseCase)
