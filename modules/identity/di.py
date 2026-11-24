from dishka import Provider, Scope, provide

from core.config import redis_settings
from modules.identity.domain.interfaces import IExternalUserDirectoryService
from modules.identity.services.external_user_service import (
    ExternalUserDirectoryService,
)
from modules.identity.use_cases import (
    GetUserDetailUseCase,
    GetUserOptionsUseCase,
    SyncSsoUserRevocationUseCase,
)


class IdentityProvider(Provider):
    """Dishka DI Provider for Identity feature module."""

    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_external_user_directory(self) -> IExternalUserDirectoryService:
        redis_client = redis_settings.get_async_client()
        return ExternalUserDirectoryService(redis_client=redis_client)

    get_user_options_uc = provide(GetUserOptionsUseCase)
    get_user_detail_uc = provide(GetUserDetailUseCase)
    sync_sso_user_revocation_uc = provide(SyncSsoUserRevocationUseCase)
