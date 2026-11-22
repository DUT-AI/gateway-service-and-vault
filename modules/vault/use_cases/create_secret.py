from modules.vault.domain.entities import ConfigChangeEvent, SecretItemEntity
from modules.vault.domain.interfaces import ISecretRepository, IVaultBroadcaster
from modules.vault.services.encryption import VaultEncryptionService


class CreateSecretUseCase:
    """Encrypts and persists a secret key-value pair under a specific scope, and broadcasts changes."""

    def __init__(
        self,
        secret_repo: ISecretRepository,
        encryption_service: VaultEncryptionService,
        broadcaster: IVaultBroadcaster,
    ) -> None:
        self.secret_repo = secret_repo
        self.encryption_service = encryption_service
        self.broadcaster = broadcaster

    async def execute(
        self,
        project_id: str,
        scope_name: str,
        key: str,
        value: str,
        actor: str = "",
    ) -> SecretItemEntity:
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

        event = ConfigChangeEvent(
            project_id=project_id,
            scope_name=scope_name,
            changed_keys=[key],
            new_version=secret.version,
            actor=actor,
        )
        await self.broadcaster.publish_secret_change(event)

        return secret
