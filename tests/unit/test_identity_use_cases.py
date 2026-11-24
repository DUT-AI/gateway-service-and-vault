import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from modules.gateway.domain.entities import ClientType, RegisteredClientEntity
from modules.identity.services.external_user_service import (
    ExternalUserDirectoryService,
)
from modules.identity.use_cases import SyncSsoUserRevocationUseCase


class FakeRedis:
    """In-memory Redis fake for unit testing cache behavior."""

    def __init__(self) -> None:
        self.store: dict[str, str] = {}
        self.should_raise: bool = False

    async def get(self, key: str) -> str | None:
        if self.should_raise:
            raise ConnectionError("Redis connection refused")
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        if self.should_raise:
            raise ConnectionError("Redis connection refused")
        self.store[key] = value

    async def delete(self, *keys: str) -> int:
        if self.should_raise:
            raise ConnectionError("Redis connection refused")
        deleted = 0
        for k in keys:
            if k in self.store:
                del self.store[k]
                deleted += 1
        return deleted

    async def scan_iter(self, match: str):
        if self.should_raise:
            raise ConnectionError("Redis connection refused")
        prefix = match.rstrip("*")
        for k in list(self.store.keys()):
            if k.startswith(prefix):
                yield k


@pytest.mark.asyncio
async def test_external_user_service_cache_hit_options():
    fake_redis = FakeRedis()
    service = ExternalUserDirectoryService(redis_client=fake_redis)

    cached_items = [
        {"id": 1, "name": "User One", "email": "user1@example.com", "avatar_url": None},
        {"id": 2, "name": "User Two", "email": "user2@example.com", "avatar_url": None},
    ]
    await fake_redis.set("identity:users:options", json.dumps(cached_items))

    # Should hit cache directly without making any HTTP request
    res = await service.get_user_options()
    assert len(res) == 2
    assert res[0].id == 1
    assert res[0].name == "User One"
    assert res[1].id == 2


@pytest.mark.asyncio
async def test_external_user_service_cache_miss_populates_redis():
    fake_redis = FakeRedis()
    service = ExternalUserDirectoryService(redis_client=fake_redis)

    mock_response = httpx.Response(
        status_code=200,
        json={
            "data": [{"id": 99, "name": "Fetched User", "email": "fetched@example.com"}]
        },
        request=httpx.Request("GET", "https://manage.dutai.io.vn/api/v1/users/options"),
    )

    with patch.object(httpx.AsyncClient, "get", AsyncMock(return_value=mock_response)):
        res = await service.get_user_options()
        assert len(res) == 1
        assert res[0].id == 99
        assert res[0].name == "Fetched User"

    # Verify cached in Redis
    cached = await fake_redis.get("identity:users:options")
    assert cached is not None
    data = json.loads(cached)
    assert data[0]["id"] == 99


@pytest.mark.asyncio
async def test_external_user_service_cache_hit_user_detail():
    fake_redis = FakeRedis()
    service = ExternalUserDirectoryService(redis_client=fake_redis)

    cached_detail = {
        "id": 42,
        "name": "Jane Doe",
        "email": "jane@example.com",
        "status": "ACTIVE",
        "phone_number": "123456789",
        "role_ids": [1],
        "role_names": ["admin"],
        "permissions": ["*"],
        "avatar_url": None,
        "discord_id": None,
        "zalo_bot_id": None,
        "check_in_card_code_configured": False,
    }
    await fake_redis.set("identity:users:detail:42", json.dumps(cached_detail))

    # Should hit cache directly without HTTP call
    user = await service.get_user_by_id(42)
    assert user is not None
    assert user.id == 42
    assert user.name == "Jane Doe"
    assert user.role_names == ["admin"]


@pytest.mark.asyncio
async def test_external_user_service_fail_open_on_redis_error():
    fake_redis = FakeRedis()
    fake_redis.should_raise = True  # Redis throws errors
    service = ExternalUserDirectoryService(redis_client=fake_redis)

    mock_response = httpx.Response(
        status_code=200,
        json={
            "data": {"id": 77, "name": "FailOpen User", "email": "failopen@example.com"}
        },
        request=httpx.Request("GET", "https://manage.dutai.io.vn/api/v1/users/77"),
    )

    with patch.object(httpx.AsyncClient, "get", AsyncMock(return_value=mock_response)):
        # Should not crash on Redis failure; fails open to HTTP
        user = await service.get_user_by_id(77)
        assert user is not None
        assert user.id == 77
        assert user.name == "FailOpen User"


@pytest.mark.asyncio
async def test_external_user_service_invalidate_cache():
    fake_redis = FakeRedis()
    service = ExternalUserDirectoryService(redis_client=fake_redis)

    await fake_redis.set("identity:users:options", "[]")
    await fake_redis.set("identity:users:detail:1", "{}")
    await fake_redis.set("identity:users:detail:2", "{}")

    # Invalidate single user
    await service.invalidate_cache(user_id=1)
    assert await fake_redis.get("identity:users:options") is None
    assert await fake_redis.get("identity:users:detail:1") is None
    assert await fake_redis.get("identity:users:detail:2") is not None

    # Invalidate all users
    await service.invalidate_cache(user_id=None)
    assert await fake_redis.get("identity:users:detail:2") is None


@pytest.mark.asyncio
async def test_sync_sso_user_revocation_invalidates_cache():
    client_repo = AsyncMock()
    key_repo = AsyncMock()
    audit_repo = AsyncMock()
    directory_service = AsyncMock()

    client = RegisteredClientEntity(
        id="client-1",
        name="Laptop",
        client_type=ClientType.USER_DEVICE,
        cert_fingerprint="fp-1",
        cert_serial="serial-1",
        expires_at=datetime.now(UTC),
        owner_id="101",
        is_revoked=False,
    )
    client_repo.list_by_owner_id.return_value = [client]
    client_repo.revoke_client.return_value = True

    uc = SyncSsoUserRevocationUseCase(
        client_repo=client_repo,
        key_repo=key_repo,
        audit_repo=audit_repo,
        directory_service=directory_service,
    )

    res = await uc.execute(user_id=101)
    assert res["user_id"] == 101
    assert res["revoked_clients_count"] == 1

    client_repo.revoke_client.assert_awaited_once_with("client-1")
    key_repo.revoke_all_by_client.assert_awaited_once_with("client-1")
    directory_service.invalidate_cache.assert_awaited_once_with(101)
