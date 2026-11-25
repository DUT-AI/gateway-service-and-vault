from loguru import logger

from modules.vault.domain.interfaces import (
    IKeyPermissionRepository,
    ISecretRepository,
)
from modules.vault.services.encryption import VaultEncryptionService
from modules.vault.use_cases.exceptions import ScopePermissionDeniedError


class GetSecretsByScopeUseCase:
    """Enforces identity-based granular key access and decrypts authorized secrets into memory."""

    def __init__(
        self,
        secret_repo: ISecretRepository,
        encryption_service: VaultEncryptionService,
        permission_repo: IKeyPermissionRepository,
    ) -> None:
        self.secret_repo = secret_repo
        self.encryption_service = encryption_service
        self.permission_repo = permission_repo

    async def execute(
        self,
        project_id: str,
        caller_identity_id: str,
        requested_scope: str | None = None,
        requested_key: str | None = None,
        bypass_key_acl: bool = False,
    ) -> dict[str, dict[str, str]]:
        # Resolve permitted keys for this identity in the project
        permitted_keys = await self.permission_repo.get_permitted_keys_for_identity(
            project_id=project_id,
            identity_id=caller_identity_id,
        )
        has_wildcard = bypass_key_acl or "*" in permitted_keys

        # If a specific key is requested, verify permission immediately
        if requested_key and not has_wildcard and requested_key not in permitted_keys:
            raise ScopePermissionDeniedError(
                f"Access denied: Identity does not have permission to access secret key '{requested_key}'"
            )

        # Deny-by-default: If identity has no permitted keys and not admin/wildcard, return empty scopes
        if not permitted_keys and not has_wildcard:
            return {}

        scopes = await self.secret_repo.list_scopes(project_id)
        result: dict[str, dict[str, str]] = {}

        for scope in scopes:
            if requested_scope and scope.name.lower() != requested_scope.lower():
                continue

            secrets = await self.secret_repo.get_secrets_by_scope(
                project_id, scope.name
            )
            scope_dict: dict[str, str] = {}

            for sec in secrets:
                # Key-level permission check: omit unauthorized keys completely
                if not has_wildcard and sec.key not in permitted_keys:
                    continue
                if requested_key and sec.key != requested_key:
                    continue

                ad = f"{project_id}:{scope.name}:{sec.key}"
                try:
                    decrypted = self.encryption_service.decrypt(
                        sec.encrypted_value,
                        sec.nonce,
                        sec.auth_tag,
                        associated_data=ad,
                    )
                    scope_dict[sec.key] = decrypted
                except Exception as err:
                    logger.warning(f"Decryption failed for key {sec.key}: {err}")
                    continue

            if scope_dict:
                result[scope.name] = scope_dict

        return result
