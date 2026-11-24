from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.security.ca import PrivateCA
from modules.gateway.client.apisix_client import ApisixAdminClient
from modules.gateway.domain.interfaces import (
    IAuditEventRepository,
    IProjectRepository,
    IQuotaPolicyRepository,
    IQuotaUsageTracker,
    IRegisteredClientRepository,
    IUpstreamServiceRepository,
    IVirtualAccessKeyRepository,
)
from modules.gateway.repository import (
    RedisQuotaUsageTracker,
    SqlAuditEventRepository,
    SqlProjectRepository,
    SqlQuotaPolicyRepository,
    SqlRegisteredClientRepository,
    SqlUpstreamServiceRepository,
    SqlVirtualAccessKeyRepository,
)
from modules.gateway.use_cases import (
    BindServiceToProjectUseCase,
    CreateUpstreamServiceUseCase,
    GenerateVirtualKeyUseCase,
    GetProjectServiceUsageUseCase,
    GetProjectUseCase,
    GetSecurityAlertsUseCase,
    ListAuditEventsUseCase,
    ListProjectAllowedServicesUseCase,
    ListProjectsUseCase,
    ListRegisteredClientsUseCase,
    ListUpstreamServicesUseCase,
    ListVirtualKeysUseCase,
    RegisterClientUseCase,
    RevokeClientUseCase,
    RevokeVirtualKeyUseCase,
    UnbindServiceFromProjectUseCase,
    UpdateProjectServiceQuotaUseCase,
    VerifyIdentityBindingUseCase,
)


class GatewayProvider(Provider):
    """Dishka DI Provider for Gateway feature module."""

    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_ca(self) -> PrivateCA:
        return PrivateCA()

    @provide(scope=Scope.APP)
    def get_apisix_client(self) -> ApisixAdminClient:
        return ApisixAdminClient()

    @provide(scope=Scope.APP)
    def get_quota_tracker(self) -> IQuotaUsageTracker:
        return RedisQuotaUsageTracker()

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

    @provide
    def get_quota_policy_repo(self, session: AsyncSession) -> IQuotaPolicyRepository:
        return SqlQuotaPolicyRepository(session)

    @provide
    def get_audit_repo(self, session: AsyncSession) -> IAuditEventRepository:
        return SqlAuditEventRepository(session)

    register_client_uc = provide(RegisterClientUseCase)
    generate_key_uc = provide(GenerateVirtualKeyUseCase)
    verify_binding_uc = provide(VerifyIdentityBindingUseCase)
    list_projects_uc = provide(ListProjectsUseCase)
    get_project_uc = provide(GetProjectUseCase)
    list_clients_uc = provide(ListRegisteredClientsUseCase)
    revoke_client_uc = provide(RevokeClientUseCase)
    list_virtual_keys_uc = provide(ListVirtualKeysUseCase)
    revoke_virtual_key_uc = provide(RevokeVirtualKeyUseCase)
    list_services_uc = provide(ListUpstreamServicesUseCase)
    create_service_uc = provide(CreateUpstreamServiceUseCase)
    list_allowed_services_uc = provide(ListProjectAllowedServicesUseCase)
    bind_service_uc = provide(BindServiceToProjectUseCase)
    unbind_service_uc = provide(UnbindServiceFromProjectUseCase)
    update_quota_uc = provide(UpdateProjectServiceQuotaUseCase)
    get_service_usage_uc = provide(GetProjectServiceUsageUseCase)
    list_audit_events_uc = provide(ListAuditEventsUseCase)
    get_security_alerts_uc = provide(GetSecurityAlertsUseCase)
