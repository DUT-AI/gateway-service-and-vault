from abc import ABC, abstractmethod

from modules.gateway.domain.entities import (
    ClientType,
    ProjectEntity,
    RegisteredClientEntity,
    UpstreamServiceEntity,
    VirtualAccessKeyEntity,
)


class IProjectRepository(ABC):
    @abstractmethod
    async def get_by_id(self, project_id: str) -> ProjectEntity | None: ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> ProjectEntity | None: ...

    @abstractmethod
    async def create(
        self, name: str, slug: str, description: str | None = None
    ) -> ProjectEntity: ...

    @abstractmethod
    async def list_all(self) -> list[ProjectEntity]: ...


class IRegisteredClientRepository(ABC):
    @abstractmethod
    async def get_by_id(self, client_id: str) -> RegisteredClientEntity | None: ...

    @abstractmethod
    async def get_by_cert_fingerprint(
        self, cert_fingerprint: str
    ) -> RegisteredClientEntity | None: ...

    @abstractmethod
    async def create(
        self,
        name: str,
        client_type: ClientType,
        owner_id: str,
        cert_fingerprint: str,
        cert_serial: str,
        expires_at,
    ) -> RegisteredClientEntity: ...

    @abstractmethod
    async def list_all(self) -> list[RegisteredClientEntity]: ...


class IVirtualAccessKeyRepository(ABC):
    @abstractmethod
    async def get_by_key_hash(self, key_hash: str) -> VirtualAccessKeyEntity | None: ...

    @abstractmethod
    async def get_active_by_client_and_project(
        self, client_id: str, project_id: str
    ) -> VirtualAccessKeyEntity | None: ...

    @abstractmethod
    async def create(
        self,
        key_hash: str,
        key_prefix: str,
        client_id: str,
        project_id: str,
    ) -> VirtualAccessKeyEntity: ...

    @abstractmethod
    async def revoke_active_keys(self, client_id: str, project_id: str) -> int: ...

    @abstractmethod
    async def list_by_project(
        self, project_id: str
    ) -> list[VirtualAccessKeyEntity]: ...

    @abstractmethod
    async def revoke_by_id(self, key_id: str) -> bool: ...


class IUpstreamServiceRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[UpstreamServiceEntity]: ...

    @abstractmethod
    async def get_by_id(self, service_id: str) -> UpstreamServiceEntity | None: ...

    @abstractmethod
    async def create(
        self,
        name: str,
        slug: str,
        base_url: str,
        auth_type: str,
        encrypted_credential: str,
        timeout_seconds: int = 30,
    ) -> UpstreamServiceEntity: ...
