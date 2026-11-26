from core.exceptions.base import EntityNotFoundError, ForbiddenError
from modules.vault.domain.entities import ConfigChangeEvent
from modules.vault.domain.interfaces import (
    IKeyPermissionRepository,
    ISecretRepository,
    IVaultBroadcaster,
)


class DeleteSecretUseCase:
    """Deletes a secret key from a project scope, enforces key ACL, and broadcasts change."""

    def __init__(
        self,
        secret_repo: ISecretRepository,
        permission_repo: IKeyPermissionRepository,
        broadcaster: IVaultBroadcaster,
    ) -> None:
        self.secret_repo = secret_repo
        self.permission_repo = permission_repo
        self.broadcaster = broadcaster

    async def execute(
        self,
        project_id: str,
        scope_name: str,
        key: str,
        actor: str = "",
        require_permission_for_identity: str | None = None,
    ) -> None:
        normalized_key = key.strip().upper()
        normalized_scope = scope_name.strip()

        if require_permission_for_identity is not None:
            permitted = await self.permission_repo.get_permitted_keys_for_identity(
                project_id=project_id,
                identity_id=require_permission_for_identity,
            )
            if normalized_key not in permitted:
                raise ForbiddenError(
                    f"You do not have permission to delete secret '{normalized_key}'"
                )

        deleted = await self.secret_repo.delete_secret(
            project_id=project_id,
            scope_name=normalized_scope,
            key=normalized_key,
        )
        if not deleted:
            raise EntityNotFoundError(
                f"Secret '{normalized_key}' not found in scope '{normalized_scope}'"
            )

        event = ConfigChangeEvent(
            project_id=project_id,
            scope_name=normalized_scope,
            changed_keys=[normalized_key],
            new_version=0,
            actor=actor,
        )
        await self.broadcaster.publish_secret_change(event)
