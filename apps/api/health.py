import redis.asyncio as aioredis
from sqlalchemy import text

from core.config import redis_settings
from core.database.session import AsyncSessionLocal


async def check_database() -> tuple[bool, str]:
    """Asynchronously test database connection."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            if result.scalar() == 1:
                return True, "ok"
            return False, "error: unexpected query result"
    except Exception as e:
        return False, f"error: {e}"


async def check_redis() -> tuple[bool, str]:
    """Asynchronously test Redis connection."""
    try:
        client = aioredis.from_url(redis_settings.redis_url, socket_timeout=3.0)
        pong = await client.ping()
        await client.aclose()
        if pong:
            return True, "ok"
        return False, "error: ping failed"
    except Exception as e:
        return False, f"error: {e}"
