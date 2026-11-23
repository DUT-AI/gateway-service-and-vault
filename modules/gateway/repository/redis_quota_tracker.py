"""Redis-backed real-time request quota usage tracker."""

import logging
from datetime import UTC, datetime

import redis.asyncio as aioredis

from core.config import redis_settings
from modules.gateway.domain.interfaces import IQuotaUsageTracker

logger = logging.getLogger("quota_tracker")


class RedisQuotaUsageTracker(IQuotaUsageTracker):
    """Tracks and enforces daily API request quotas using Redis atomic operations."""

    def __init__(self, redis_client: aioredis.Redis | None = None) -> None:
        self._redis = redis_client

    @property
    def redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = redis_settings.get_async_client()
        return self._redis

    @staticmethod
    def _make_key(project_id: str, service_id: str, date_str: str | None = None) -> str:
        date_str = date_str or datetime.now(UTC).strftime("%Y%m%d")
        return f"gateway:quota:{project_id}:{service_id}:{date_str}"

    async def get_usage(self, project_id: str, service_id: str) -> int:
        """Retrieve current day's request usage count from Redis."""
        key = self._make_key(project_id, service_id)
        try:
            val = await self.redis.get(key)
            return int(val) if val else 0
        except Exception as e:
            logger.warning("Failed to get quota usage from Redis (fail-open): %s", e)
            return 0

    async def increment_and_check(
        self, project_id: str, service_id: str, quota_daily: int
    ) -> tuple[int, bool]:
        """Atomically increment daily usage counter and check whether within ceiling.

        Returns (new_count, is_within_quota).
        """
        key = self._make_key(project_id, service_id)
        try:
            current = await self.redis.incr(key)
            if current == 1:
                # 48 hours TTL to allow rollover inspection and automatic garbage collection
                await self.redis.expire(key, 172800)
            is_within = current <= quota_daily
            return current, is_within
        except Exception as e:
            logger.warning(
                "Failed to increment quota counter in Redis (fail-open): %s", e
            )
            return 0, True
