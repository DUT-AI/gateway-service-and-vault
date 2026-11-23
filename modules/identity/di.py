from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from modules.identity.domain.interfaces import (
    IExternalUserDirectoryService,
    IUserRepository,
)
from modules.identity.repository.user_repository import SqlUserRepository
from modules.identity.services.external_user_service import (
    ExternalUserDirectoryService,
)
from modules.identity.use_cases import (
    GetCurrentUserUseCase,
    GetUserDetailUseCase,
    GetUserOptionsUseCase,
    ListUsersUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
    SyncSsoUserRevocationUseCase,
)


class IdentityProvider(Provider):
    """Dishka DI Provider for Identity feature module."""

    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_external_user_directory(self) -> IExternalUserDirectoryService:
        return ExternalUserDirectoryService()

    @provide
    def get_user_repository(self, session: AsyncSession) -> IUserRepository:
        return SqlUserRepository(session)

    register_user_uc = provide(RegisterUserUseCase)
    login_user_uc = provide(LoginUserUseCase)
    get_current_user_uc = provide(GetCurrentUserUseCase)
    list_users_uc = provide(ListUsersUseCase)
    get_user_options_uc = provide(GetUserOptionsUseCase)
    get_user_detail_uc = provide(GetUserDetailUseCase)
    sync_sso_user_revocation_uc = provide(SyncSsoUserRevocationUseCase)
