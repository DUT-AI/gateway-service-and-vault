import asyncio
from typing import Any

from arq import run_worker
from arq.connections import RedisSettings
from loguru import logger

from core.config import redis_settings
from core.database.session import AsyncSessionLocal
from core.events.processor import OutboxProcessor

outbox_processor = OutboxProcessor()


async def send_welcome_email(ctx: dict[str, Any], user_id: int, email: str) -> bool:
    """Send welcome email to a newly registered user."""
    logger.info(f"[Worker] Sending welcome email to user {user_id} ({email})...")
    # Simulate email sending
    await asyncio.sleep(0.01)
    logger.info(f"[Worker] Welcome email sent successfully to {email}")
    return True


async def handle_user_registered(payload: dict[str, Any]) -> None:
    """Handler for user.registered outbox event."""
    user_id = payload.get("user_id")
    email = payload.get("email")
    logger.info(
        f"[Worker] Dispatched user.registered event for user {user_id} ({email})"
    )


# Register default outbox handlers
outbox_processor.register_handler("user.registered", handle_user_registered)


async def process_outbox_events(ctx: dict[str, Any], batch_size: int = 50) -> int:
    """Process pending domain events stored in the outbox table."""
    logger.info(f"[Worker] Scanning outbox for up to {batch_size} pending events...")
    async with AsyncSessionLocal() as session:
        count = await outbox_processor.process_pending_batch(session, limit=batch_size)
        if count > 0:
            logger.info(f"[Worker] Successfully processed {count} outbox event(s).")
        return count


async def on_startup(ctx: dict[str, Any]) -> None:
    logger.info("[Worker] ARQ Background Worker starting up...")


async def on_shutdown(ctx: dict[str, Any]) -> None:
    logger.info("[Worker] ARQ Background Worker shutting down...")


class WorkerSettings:
    """ARQ Worker configuration settings."""

    functions = [send_welcome_email, process_outbox_events]  # noqa: RUF012
    on_startup = on_startup
    on_shutdown = on_shutdown
    redis_settings = RedisSettings.from_dsn(redis_settings.redis_url)
    max_jobs = 10
    job_timeout = 300


def main() -> None:
    """Start worker process."""
    run_worker(WorkerSettings)  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
