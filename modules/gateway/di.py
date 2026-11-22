from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.security.ca import PrivateCA
from modules.gateway.domain.interfaces import (
    IProjectRepository,
    IRegisteredClientRepository,
    IUpstreamServiceRepository,
    IVirtualAccessKeyRepository,
)
from modules.gateway.repository.gateway_repository import (
    SqlProjectRepository,
    SqlRegisteredClientRepository,
    SqlUpstreamServiceRepository,
    SqlVirtualAccessKeyRepository,
)
from modules.gateway.use_cases import (
    CreateUpstreamServiceUseCase,
    GenerateVirtualKeyUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    ListRegisteredClientsUseCase,
    ListUpstreamServicesUseCase,
    ListVirtualKeysUseCase,
    RegisterClientUseCase,
    RevokeVirtualKeyUseCase,
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

    @provide
    def get_service_repo(self, session: AsyncSession) -> IUpstreamServiceRepository:
        return SqlUpstreamServiceRepository(session)

    register_client_uc = provide(RegisterClientUseCase)
    generate_key_uc = provide(GenerateVirtualKeyUseCase)
    verify_binding_uc = provide(VerifyIdentityBindingUseCase)
    list_projects_uc = provide(ListProjectsUseCase)
    get_project_uc = provide(GetProjectUseCase)
    list_clients_uc = provide(ListRegisteredClientsUseCase)
    list_virtual_keys_uc = provide(ListVirtualKeysUseCase)
    revoke_virtual_key_uc = provide(RevokeVirtualKeyUseCase)
    list_services_uc = provide(ListUpstreamServicesUseCase)
    create_service_uc = provide(CreateUpstreamServiceUseCase)
