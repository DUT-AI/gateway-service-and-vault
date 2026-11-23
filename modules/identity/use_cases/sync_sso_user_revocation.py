import contextlib
from datetime import UTC, datetime
from typing import Any

from core.utils.id_generator import generate_ulid
from modules.gateway.domain.entities import AuditEventEntity, ClientType
from modules.gateway.domain.interfaces import (
    IAuditEventRepository,
    IRegisteredClientRepository,
)


class SyncSsoUserRevocationUseCase:
    """Cascade revokes all registered clients and virtual keys owned by a deactivated SSO user."""

    def __init__(
        self,
        client_repo: IRegisteredClientRepository,
        audit_repo: IAuditEventRepository,
    ) -> None:
        self.client_repo = client_repo
        self.audit_repo = audit_repo

    async def execute(self, user_id: int) -> dict[str, Any]:
        owner_str = str(user_id)
        clients = await self.client_repo.list_by_owner_id(owner_str)
        revoked_count = 0

        for client in clients:
            if not client.is_revoked:
                success = await self.client_repo.revoke_client(client.id)
                if success:
                    revoked_count += 1

        # Record immutable audit log
        with contextlib.suppress(Exception):
            event = AuditEventEntity(
                id=generate_ulid(),
                timestamp=datetime.now(UTC),
                client_type=ClientType.USER_DEVICE,
                actor_id=owner_str,
                project_id="SYSTEM",
                service_id=None,
                action="SSO_USER_REVOKED",
                decision="ALLOW",
                client_ip=None,
                error_code=None,
                metadata={
                    "user_id": user_id,
                    "revoked_clients_count": revoked_count,
                    "total_clients_found": len(clients),
                },
            )
            await self.audit_repo.record_event(event)

        return {
            "user_id": user_id,
            "revoked_clients_count": revoked_count,
            "total_clients_found": len(clients),
            "message": f"Successfully revoked {revoked_count} client(s) and associated virtual keys for user {user_id}",
        }
