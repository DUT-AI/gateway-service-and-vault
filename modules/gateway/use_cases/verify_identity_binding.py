from core.security.ca import PrivateCA
from modules.gateway.domain.interfaces import (
    IProjectRepository,
    IRegisteredClientRepository,
    IVirtualAccessKeyRepository,
)
from modules.gateway.use_cases.exceptions import (
    IdentityMismatchError,
    ServiceNotPermittedError,
)


class VerifyIdentityBindingUseCase:
    """Verifies that a presented virtual key belongs to the certificate, project, and allowed service."""

    def __init__(
        self,
        key_repo: IVirtualAccessKeyRepository,
        client_repo: IRegisteredClientRepository,
        project_repo: IProjectRepository,
    ) -> None:
        self.key_repo = key_repo
        self.client_repo = client_repo
        self.project_repo = project_repo

    async def execute(
        self,
        raw_virtual_key: str,
        cert_fingerprint: str,
        project_id: str,
        service_id: str | None = None,
    ) -> bool:
        key_hash = PrivateCA.hash_virtual_key(raw_virtual_key)
        key_entity = await self.key_repo.get_by_key_hash(key_hash)

        if not key_entity or key_entity.status.value != "ACTIVE":
            raise IdentityMismatchError("Invalid or inactive virtual key")

        if key_entity.project_id != project_id:
            raise IdentityMismatchError(
                "Virtual key does not belong to requested project"
            )

        client = await self.client_repo.get_by_id(key_entity.client_id)
        if not client or client.is_revoked:
            raise IdentityMismatchError("Client is not found or revoked")

        if client.cert_fingerprint.lower() != cert_fingerprint.lower():
            raise IdentityMismatchError(
                "Client certificate does not match the virtual key binding"
            )

        if service_id and not await self.project_repo.is_service_allowed(
            project_id, service_id
        ):
            raise ServiceNotPermittedError(
                f"Upstream service '{service_id}' is not permitted for project '{project_id}'"
            )

        return True
