import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.identity.domain.entities import ExternalUserOptionEntity
from modules.identity.services.external_user_service import ExternalUserDirectoryService


@pytest.mark.asyncio
async def test_get_user_options_cache_hit():
    """Verify that cached data in Redis is returned directly without HTTP request."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = json.dumps(
        [
            {
                "id": 42,
                "name": "Cached User",
                "email": "cached@dutai.io.vn",
                "avatar_url": None,
            }
        ]
    )

    service = ExternalUserDirectoryService(redis_client=mock_redis)

    result = await service.get_user_options(auth_token="test_token")
    assert len(result) == 1
    assert isinstance(result[0], ExternalUserOptionEntity)
    assert result[0].id == 42
    assert result[0].name == "Cached User"
    mock_redis.get.assert_awaited_once_with(
        ExternalUserDirectoryService.CACHE_KEY_OPTIONS
    )


@pytest.mark.asyncio
async def test_get_user_options_cache_miss_and_store():
    """Verify that on cache miss, HTTP request is made and result is saved to Redis."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None  # Cache miss

    service = ExternalUserDirectoryService(redis_client=mock_redis)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "id": 101,
                "name": "Remote User",
                "email": "remote@dutai.io.vn",
                "avatar_url": None,
            }
        ]
    }
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await service.get_user_options(auth_token="test_token")

    assert len(result) == 1
    assert result[0].id == 101
    mock_redis.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_user_options_fail_open_on_redis_error():
    """Verify that if Redis throws an exception, service fails open to remote HTTP."""
    mock_redis = AsyncMock()
    mock_redis.get.side_effect = Exception("Redis connection refused")

    service = ExternalUserDirectoryService(redis_client=mock_redis)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "id": 99,
                "name": "Fail Open User",
                "email": "failopen@dutai.io.vn",
                "avatar_url": None,
            }
        ]
    }
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await service.get_user_options(auth_token="test_token")

    assert len(result) == 1
    assert result[0].id == 99


@pytest.mark.asyncio
async def test_invalidate_cache():
    """Verify cache invalidation for all users and specific user."""
    mock_redis = AsyncMock()
    service = ExternalUserDirectoryService(redis_client=mock_redis)

    await service.invalidate_cache(user_id=123)
    mock_redis.delete.assert_awaited_once_with(
        ExternalUserDirectoryService.CACHE_KEY_OPTIONS,
        f"{ExternalUserDirectoryService.CACHE_KEY_USER_PREFIX}123",
    )
