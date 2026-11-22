import json
from unittest.mock import AsyncMock

import pytest

from modules.vault.domain.entities import ConfigChangeEvent
from modules.vault.services.broadcaster import RedisVaultBroadcaster


@pytest.mark.asyncio
async def test_redis_vault_broadcaster_publishes_event():
    mock_redis = AsyncMock()
    mock_redis.publish.return_value = 2

    broadcaster = RedisVaultBroadcaster(mock_redis)
    event = ConfigChangeEvent(
        project_id="prj_alpha",
        scope_name="common",
        changed_keys=["DATABASE_URL", "CACHE_TTL"],
        new_version=3,
        actor="dev_user",
    )

    await broadcaster.publish_secret_change(event)

    expected_channel = "vault:project:prj_alpha:changes"
    mock_redis.publish.assert_awaited_once()
    args, _kwargs = mock_redis.publish.await_args
    assert args[0] == expected_channel

    payload = json.loads(args[1])
    assert payload["project_id"] == "prj_alpha"
    assert payload["scope_name"] == "common"
    assert payload["changed_keys"] == ["DATABASE_URL", "CACHE_TTL"]
    assert payload["new_version"] == 3
    assert payload["actor"] == "dev_user"
    assert payload["event_id"] == event.event_id
