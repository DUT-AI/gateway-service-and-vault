from modules.vault.use_cases.create_secret import CreateSecretUseCase
from modules.vault.use_cases.create_secrets_batch import CreateSecretsBatchUseCase
from modules.vault.use_cases.exceptions import ScopePermissionDeniedError
from modules.vault.use_cases.get_secrets_by_scope import GetSecretsByScopeUseCase
from modules.vault.use_cases.grant_key_permission import GrantKeyPermissionUseCase
from modules.vault.use_cases.list_identity_permissions import (
    ListIdentityPermissionsUseCase,
)
from modules.vault.use_cases.list_scopes import ListScopesUseCase
from modules.vault.use_cases.revoke_key_permission import RevokeKeyPermissionUseCase

__all__ = [
    "CreateSecretUseCase",
    "CreateSecretsBatchUseCase",
    "GetSecretsByScopeUseCase",
    "GrantKeyPermissionUseCase",
    "ListIdentityPermissionsUseCase",
    "ListScopesUseCase",
    "RevokeKeyPermissionUseCase",
    "ScopePermissionDeniedError",
]
