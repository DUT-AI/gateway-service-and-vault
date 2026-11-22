from pathlib import Path
from typing import Any

import redis.asyncio as aioredis
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class RedisSettings(BaseSettings):
    """Redis & Task Queue Configuration."""

    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env",),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    redis_url: str = "redis://localhost:6379/0"

    def get_async_client(self, **kwargs: Any) -> aioredis.Redis:
        """Create an asynchronous Redis client instance."""
        options: dict[str, Any] = {"decode_responses": True}
        options.update(kwargs)
        return aioredis.from_url(self.redis_url, **options)
