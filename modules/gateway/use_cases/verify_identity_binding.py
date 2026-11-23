import contextlib
from datetime import UTC, datetime

from core.security.ca import PrivateCA
from core.utils.id_generator import generate_ulid
from modules.gateway.domain.entities import AuditEventEntity, ClientType
from modules.gateway.domain.interfaces import (
    IAuditEventRepository,
    IProjectRepository,
    IQuotaUsageTracker,
    IRegisteredClientRepository,
    IUpstreamServiceRepository,
    IVirtualAccessKeyRepository,
)
from modules.gateway.use_cases.exceptions import (
    DailyQuotaExceededError,
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
        service_repo: IUpstreamServiceRepository,
        quota_tracker: IQuotaUsageTracker,
        audit_repo: IAuditEventRepository,
    ) -> None:
        self.key_repo = key_repo
        self.client_repo = client_repo
        self.project_repo = project_repo
        self.service_repo = service_repo
        self.quota_tracker = quota_tracker
        self.audit_repo = audit_repo

    async def _record_audit(
        self,
        decision: str,  # ALLOW, DENY
        client_type: ClientType,
        actor_id: str,
        project_id: str,
        service_id: str | None,
        client_ip: str | None,
        error_code: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        with contextlib.suppress(Exception):
            event = AuditEventEntity(
                id=generate_ulid(),
                timestamp=datetime.now(UTC),
                client_type=client_type,
                actor_id=actor_id,
                project_id=project_id,
                service_id=service_id,
                action="GATEWAY_ACCESS",
                decision=decision,
                client_ip=client_ip,
                error_code=error_code,
                metadata=metadata or {},
            )
            await self.audit_repo.record_event(event)

    async def execute(
        self,
        raw_virtual_key: str,
        cert_fingerprint: str,
        project_id: str,
        service_id: str | None = None,
        service_slug: str | None = None,
        client_raw_cert: str | None = None,
        client_ip: str | None = None,
    ) -> bool:
        key_hash = PrivateCA.hash_virtual_key(raw_virtual_key)
        key_entity = await self.key_repo.get_by_key_hash(key_hash)

        if not key_entity or key_entity.status.value != "ACTIVE":
            await self._record_audit(
                decision="DENY",
                client_type=ClientType.USER_DEVICE,
                actor_id="UNKNOWN",
                project_id=project_id,
                service_id=service_id,
                client_ip=client_ip,
                error_code="IDENTITY_MISMATCH",
                metadata={"reason": "Invalid or inactive virtual key"},
            )
            raise IdentityMismatchError("Invalid or inactive virtual key")

        if key_entity.project_id != project_id:
            await self._record_audit(
                decision="DENY",
                client_type=ClientType.USER_DEVICE,
                actor_id=key_entity.client_id,
                project_id=project_id,
                service_id=service_id,
                client_ip=client_ip,
                error_code="IDENTITY_MISMATCH",
                metadata={"reason": "Virtual key does not belong to requested project"},
            )
            raise IdentityMismatchError(
                "Virtual key does not belong to requested project"
            )

        client = await self.client_repo.get_by_id(key_entity.client_id)
        if not client or client.is_revoked:
            await self._record_audit(
                decision="DENY",
                client_type=(client.client_type if client else ClientType.USER_DEVICE),
                actor_id=key_entity.client_id,
                project_id=project_id,
                service_id=service_id,
                client_ip=client_ip,
                error_code=(
                    "CLIENT_REVOKED"
                    if (client and client.is_revoked)
                    else "IDENTITY_MISMATCH"
                ),
                metadata={"reason": "Client is not found or revoked"},
            )
            raise IdentityMismatchError("Client is not found or revoked")

        if client.cert_fingerprint.lower() != cert_fingerprint.lower():
            matches = False
            if client_raw_cert:
                with contextlib.suppress(Exception):
                    computed = PrivateCA.compute_cert_fingerprint(client_raw_cert)
                    if client.cert_fingerprint.lower() == computed.lower():
                        matches = True
            if not matches:
                await self._record_audit(
                    decision="DENY",
                    client_type=client.client_type,
                    actor_id=client.id,
                    project_id=project_id,
                    service_id=service_id,
                    client_ip=client_ip,
                    error_code="IDENTITY_MISMATCH",
                    metadata={
                        "reason": "Client certificate does not match the virtual key binding",
                        "expected_fingerprint": client.cert_fingerprint,
                        "received_fingerprint": cert_fingerprint,
                    },
                )
                raise IdentityMismatchError(
                    "Client certificate does not match the virtual key binding"
                )

        # Resolve target service if service_slug is provided
        target_service_id = service_id
        if not target_service_id and service_slug:
            service = await self.service_repo.get_by_slug(service_slug)
            if not service or not service.is_active:
                await self._record_audit(
                    decision="DENY",
                    client_type=client.client_type,
                    actor_id=client.id,
                    project_id=project_id,
                    service_id=None,
                    client_ip=client_ip,
                    error_code="SERVICE_NOT_ALLOWED",
                    metadata={
                        "reason": f"Upstream service '{service_slug}' not found or inactive"
                    },
                )
                raise ServiceNotPermittedError(
                    f"Upstream service '{service_slug}' not found or inactive"
                )
            target_service_id = service.id

        if target_service_id and not await self.project_repo.is_service_allowed(
            project_id, target_service_id
        ):
            await self._record_audit(
                decision="DENY",
                client_type=client.client_type,
                actor_id=client.id,
                project_id=project_id,
                service_id=target_service_id,
                client_ip=client_ip,
                error_code="SERVICE_NOT_ALLOWED",
                metadata={
                    "reason": f"Upstream service '{service_slug or target_service_id}' is not permitted for project '{project_id}'"
                },
            )
            raise ServiceNotPermittedError(
                f"Upstream service '{service_slug or target_service_id}' is not permitted for project '{project_id}'"
            )

        # Enforce daily quota ceiling if service is configured
        if target_service_id and self.quota_tracker:
            policy = await self.project_repo.get_service_quota(
                project_id, target_service_id
            )
            if policy and policy.is_active:
                current_count, is_within = await self.quota_tracker.increment_and_check(
                    project_id=project_id,
                    service_id=target_service_id,
                    quota_daily=policy.quota_daily,
                )
                if not is_within:
                    await self._record_audit(
                        decision="DENY",
                        client_type=client.client_type,
                        actor_id=client.id,
                        project_id=project_id,
                        service_id=target_service_id,
                        client_ip=client_ip,
                        error_code="DAILY_QUOTA_EXCEEDED",
                        metadata={
                            "usage_today": current_count,
                            "quota_daily": policy.quota_daily,
                        },
                    )
                    raise DailyQuotaExceededError(
                        f"Daily request quota exceeded for service '{service_slug or target_service_id}' (limit: {policy.quota_daily})",
                        details={
                            "usage_today": current_count,
                            "quota_daily": policy.quota_daily,
                            "service_id": target_service_id,
                            "project_id": project_id,
                        },
                    )

        # Successful verification -> ALLOW
        await self._record_audit(
            decision="ALLOW",
            client_type=client.client_type,
            actor_id=client.id,
            project_id=project_id,
            service_id=target_service_id,
            client_ip=client_ip,
            error_code=None,
        )

        return True
