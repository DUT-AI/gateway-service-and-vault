from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.vault.domain.entities import (
    KeyPermissionEntity,
    SecretItemEntity,
    SecretScopeEntity,
)
from modules.vault.use_cases import (
    GetSecretsByScopeUseCase,
    GrantKeyPermissionUseCase,
    ListIdentityPermissionsUseCase,
    RevokeKeyPermissionUseCase,
    ScopePermissionDeniedError,
)


@pytest.mark.asyncio
async def test_grant_key_permission_use_case():
    repo = AsyncMock()
    now = datetime.now(UTC)
    expected = KeyPermissionEntity(
        id="perm_1",
        project_id="proj_1",
        identity_id="client_worker",
        secret_key="REDIS_PASSWORD",
        identity_type="client",
        granted_by="admin",
        created_at=now,
        updated_at=now,
    )
    repo.grant_key_permission.return_value = expected

    uc = GrantKeyPermissionUseCase(permission_repo=repo)
    result = await uc.execute(
        project_id="proj_1",
        identity_id="client_worker",
        secret_key="REDIS_PASSWORD",
        identity_type="client",
        granted_by="admin",
    )
    assert result == expected
    repo.grant_key_permission.assert_awaited_once_with(
        project_id="proj_1",
        identity_id="client_worker",
        secret_key="REDIS_PASSWORD",
        identity_type="client",
        granted_by="admin",
    )


@pytest.mark.asyncio
async def test_revoke_key_permission_use_case():
    repo = AsyncMock()
    repo.revoke_key_permission.return_value = True

    uc = RevokeKeyPermissionUseCase(permission_repo=repo)
    result = await uc.execute(
        project_id="proj_1",
        identity_id="client_worker",
        secret_key="REDIS_PASSWORD",
    )
    assert result is True
    repo.revoke_key_permission.assert_awaited_once_with(
        project_id="proj_1",
        identity_id="client_worker",
        secret_key="REDIS_PASSWORD",
    )


@pytest.mark.asyncio
async def test_list_identity_permissions_use_case():
    repo = AsyncMock()
    repo.get_permitted_keys_for_identity.return_value = ["KEY_A", "KEY_B"]

    uc = ListIdentityPermissionsUseCase(permission_repo=repo)
    result = await uc.execute(project_id="proj_1", identity_id="client_worker")
    assert result == ["KEY_A", "KEY_B"]
    repo.get_permitted_keys_for_identity.assert_awaited_once_with(
        project_id="proj_1", identity_id="client_worker"
    )


@pytest.mark.asyncio
async def test_get_secrets_deny_by_default_when_no_permissions():
    repo = AsyncMock()
    repo.get_permitted_keys_for_identity.return_value = []
    enc_service = MagicMock()

    uc = GetSecretsByScopeUseCase(
        secret_repo=repo,
        encryption_service=enc_service,
        permission_repo=repo,
    )
    result = await uc.execute(project_id="proj_1", caller_identity_id="unauthorized_id")
    assert result == {}


@pytest.mark.asyncio
async def test_get_secrets_raises_403_on_unauthorized_single_key():
    repo = AsyncMock()
    repo.get_permitted_keys_for_identity.return_value = ["ALLOWED_KEY"]
    enc_service = MagicMock()

    uc = GetSecretsByScopeUseCase(
        secret_repo=repo,
        encryption_service=enc_service,
        permission_repo=repo,
    )
    with pytest.raises(ScopePermissionDeniedError):
        await uc.execute(
            project_id="proj_1",
            caller_identity_id="dev_user",
            requested_key="FORBIDDEN_KEY",
        )


@pytest.mark.asyncio
async def test_get_secrets_filters_decrypted_secrets_by_permitted_keys():
    repo = AsyncMock()
    repo.get_permitted_keys_for_identity.return_value = ["KEY_1"]
    repo.list_scopes.return_value = [
        SecretScopeEntity(id="s1", project_id="proj_1", name="app")
    ]
    repo.get_secrets_by_scope.return_value = [
        SecretItemEntity(
            id="sec1",
            project_id="proj_1",
            scope_id="s1",
            key="KEY_1",
            encrypted_value="enc1",
            nonce="n1",
            auth_tag="t1",
            version=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        SecretItemEntity(
            id="sec2",
            project_id="proj_1",
            scope_id="s1",
            key="KEY_SECRET",
            encrypted_value="enc2",
            nonce="n2",
            auth_tag="t2",
            version=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]

    enc_service = MagicMock()
    enc_service.decrypt.return_value = "decrypted_key_1"

    uc = GetSecretsByScopeUseCase(
        secret_repo=repo,
        encryption_service=enc_service,
        permission_repo=repo,
    )
    result = await uc.execute(project_id="proj_1", caller_identity_id="dev_user")
    assert result == {"app": {"KEY_1": "decrypted_key_1"}}
    assert "KEY_SECRET" not in result["app"]
