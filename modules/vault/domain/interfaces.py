from abc import ABC, abstractmethod
from typing import Protocol

from modules.vault.domain.entities import (
    ConfigChangeEvent,
    KeyPermissionEntity,
    SecretItemEntity,
    SecretScopeEntity,
)


class ISecretRepository(ABC):
    @abstractmethod
    async def get_or_create_scope(
        self, project_id: str, scope_name: str, description: str | None = None
    ) -> SecretScopeEntity: ...

    @abstractmethod
    async def list_scopes(self, project_id: str) -> list[SecretScopeEntity]: ...

    @abstractmethod
    async def get_secrets_by_scope(
        self, project_id: str, scope_name: str
    ) -> list[SecretItemEntity]: ...

    @abstractmethod
    async def upsert_secret(
        self,
        project_id: str,
        scope_name: str,
        key: str,
        encrypted_value: str,
        nonce: str,
        auth_tag: str,
        actor: str = "",
    ) -> SecretItemEntity: ...

    @abstractmethod
    async def grant_key_permission(
        self,
        project_id: str,
        identity_id: str,
        secret_key: str,
        identity_type: str = "client",
        granted_by: str = "",
    ) -> KeyPermissionEntity: ...

    @abstractmethod
    async def revoke_key_permission(
        self, project_id: str, identity_id: str, secret_key: str
    ) -> bool: ...

    @abstractmethod
    async def list_permissions_by_identity(
        self, project_id: str, identity_id: str
    ) -> list[str]: ...

    @abstractmethod
    async def get_permitted_keys_for_identity(
        self, project_id: str, identity_id: str
    ) -> set[str]: ...


class IVaultBroadcaster(Protocol):
    """Protocol for broadcasting secret configuration changes across instances."""

    async def publish_secret_change(self, event: ConfigChangeEvent) -> None: ...
