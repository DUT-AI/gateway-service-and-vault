from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.security.ca import PrivateCA
from modules.gateway.domain.interfaces import (
    IProjectRepository,
    IRegisteredClientRepository,
    IVirtualAccessKeyRepository,
)
from modules.gateway.repository.gateway_repository import (
    SqlProjectRepository,
    SqlRegisteredClientRepository,
    SqlVirtualAccessKeyRepository,
)
from modules.gateway.use_cases import (
    GenerateVirtualKeyUseCase,
    RegisterClientUseCase,
    VerifyIdentityBindingUseCase,
)


class GatewayProvider(Provider):
    """Dishka DI Provider for Gateway feature module."""

    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_ca(self) -> PrivateCA:
        return PrivateCA()

    @provide
    def get_project_repo(self, session: AsyncSession) -> IProjectRepository:
        return SqlProjectRepository(session)

    @provide
    def get_client_repo(self, session: AsyncSession) -> IRegisteredClientRepository:
        return SqlRegisteredClientRepository(session)

    @provide
    def get_key_repo(self, session: AsyncSession) -> IVirtualAccessKeyRepository:
        return SqlVirtualAccessKeyRepository(session)

    register_client_uc = provide(RegisterClientUseCase)
    generate_key_uc = provide(GenerateVirtualKeyUseCase)
    verify_binding_uc = provide(VerifyIdentityBindingUseCase)
