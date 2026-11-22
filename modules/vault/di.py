import redis.asyncio as aioredis
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import redis_settings, vault_settings
from modules.vault.domain.interfaces import ISecretRepository, IVaultBroadcaster
from modules.vault.repository.secret_repository import SqlSecretRepository
from modules.vault.services.broadcaster import RedisVaultBroadcaster
from modules.vault.services.encryption import VaultEncryptionService
from modules.vault.use_cases import (
    CreateSecretUseCase,
    GetSecretsByScopeUseCase,
    GrantKeyPermissionUseCase,
    ListIdentityPermissionsUseCase,
    ListScopesUseCase,
    RevokeKeyPermissionUseCase,
)


class VaultProvider(Provider):
    """Dishka DI Provider for Dynamic Vault feature module."""

    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_encryption_service(self) -> VaultEncryptionService:
        return VaultEncryptionService(master_key=vault_settings.vault_master_key)

    @provide
    def get_redis_client(self) -> aioredis.Redis:
        return redis_settings.get_async_client()

    @provide
    def get_vault_broadcaster(self, redis_client: aioredis.Redis) -> IVaultBroadcaster:
        return RedisVaultBroadcaster(redis_client=redis_client)

    @provide
    def get_secret_repo(self, session: AsyncSession) -> ISecretRepository:
        return SqlSecretRepository(session)

    create_secret_uc = provide(CreateSecretUseCase)
    get_secrets_uc = provide(GetSecretsByScopeUseCase)
    grant_key_permission_uc = provide(GrantKeyPermissionUseCase)
    revoke_key_permission_uc = provide(RevokeKeyPermissionUseCase)
    list_identity_permissions_uc = provide(ListIdentityPermissionsUseCase)
    list_scopes_uc = provide(ListScopesUseCase)
