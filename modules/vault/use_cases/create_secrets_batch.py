from modules.vault.domain.entities import ConfigChangeEvent, SecretItemEntity
from modules.vault.domain.interfaces import (
    IKeyPermissionRepository,
    ISecretRepository,
    IVaultBroadcaster,
)
from modules.vault.services.encryption import VaultEncryptionService


class CreateSecretsBatchUseCase:
    """Encrypts and persists multiple secrets under a scope in one transaction and broadcasts once."""

    def __init__(
        self,
        secret_repo: ISecretRepository,
        encryption_service: VaultEncryptionService,
        broadcaster: IVaultBroadcaster,
        permission_repo: IKeyPermissionRepository,
    ) -> None:
        self.secret_repo = secret_repo
        self.encryption_service = encryption_service
        self.broadcaster = broadcaster
        self.permission_repo = permission_repo

    async def execute(
        self,
        project_id: str,
        scope_name: str,
        items: list[tuple[str, str]],
        actor: str = "",
        grant_to_identity_id: str | None = None,
    ) -> list[SecretItemEntity]:
        created_secrets: list[SecretItemEntity] = []
        changed_keys: list[str] = []
        max_version = 1

        for key, value in items:
            ad = f"{project_id}:{scope_name}:{key}"
            ciphertext, nonce, auth_tag = self.encryption_service.encrypt(
                value, associated_data=ad
            )
            secret = await self.secret_repo.upsert_secret(
                project_id=project_id,
                scope_name=scope_name,
                key=key,
                encrypted_value=ciphertext,
                nonce=nonce,
                auth_tag=auth_tag,
                actor=actor,
            )
            if self.permission_repo and grant_to_identity_id:
                await self.permission_repo.grant_key_permission(
                    project_id=project_id,
                    identity_id=grant_to_identity_id,
                    secret_key=key,
                    identity_type="user",
                    granted_by=actor or grant_to_identity_id,
                )
            created_secrets.append(secret)
            changed_keys.append(key)
            max_version = max(max_version, secret.version)

        if changed_keys:
            event = ConfigChangeEvent(
                project_id=project_id,
                scope_name=scope_name,
                changed_keys=changed_keys,
                new_version=max_version,
                actor=actor,
            )
            await self.broadcaster.publish_secret_change(event)

        return created_secrets
