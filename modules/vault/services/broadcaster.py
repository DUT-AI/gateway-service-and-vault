import json

import redis.asyncio as aioredis
from loguru import logger

from modules.vault.domain.entities import ConfigChangeEvent
from modules.vault.domain.interfaces import IVaultBroadcaster


class RedisVaultBroadcaster(IVaultBroadcaster):
    """Broadcasts secret configuration change events via Redis Pub/Sub."""

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client

    @staticmethod
    def get_channel_name(project_id: str) -> str:
        return f"vault:project:{project_id}:changes"

    async def publish_secret_change(self, event: ConfigChangeEvent) -> None:
        channel = self.get_channel_name(event.project_id)
        payload = json.dumps(event.to_dict())
        try:
            receivers = await self._redis.publish(channel, payload)
            logger.debug(
                "Published secret change event {} to channel {} ({} subscribers)",
                event.event_id,
                channel,
                receivers,
            )
        except Exception as e:
            logger.error("Failed to publish secret change event to Redis: {}", e)
            raise
