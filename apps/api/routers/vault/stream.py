import asyncio
import json
import time
from datetime import UTC, datetime

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Header, Query
from fastapi.responses import StreamingResponse
from loguru import logger

from core.config import redis_settings
from modules.vault.domain.interfaces import ISecretRepository
from modules.vault.services.broadcaster import RedisVaultBroadcaster

router = APIRouter()


@router.get(
    "/projects/{project_id}/stream",
    summary="Server-Sent Events stream for dynamic secret configuration updates",
)
@inject
async def stream_project_secrets(
    project_id: str,
    secret_repo: FromDishka[ISecretRepository],
    scope: str | None = Query(default=None),
    identity_id: str | None = Query(default=None),
    max_events: int | None = Query(
        default=None,
        description="Max events to yield before closing stream (useful for testing)",
    ),
    x_identity_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
) -> StreamingResponse:
    """Stream real-time secret update events filtered by caller key permissions."""
    caller_id = x_identity_id or identity_id or x_user_role or "anonymous"
    permitted_keys = set(
        await secret_repo.get_permitted_keys_for_identity(
            project_id=project_id, identity_id=caller_id
        )
    )
    is_admin = caller_id.lower() in ["admin", "system"]
    has_wildcard = "*" in permitted_keys or is_admin

    async def event_generator():
        client = redis_settings.get_async_client()
        pubsub = client.pubsub()
        channel = RedisVaultBroadcaster.get_channel_name(project_id)
        await pubsub.subscribe(channel)

        yielded_count = 0

        # 1. Send initial connected event
        connected_data = json.dumps(
            {
                "project_id": project_id,
                "status": "active",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        yield f"event: connected\ndata: {connected_data}\n\n"
        yielded_count += 1
        if max_events is not None and yielded_count >= max_events:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()
            await client.aclose()
            return

        last_ping = time.monotonic()
        try:
            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=0.2
                )
                now = time.monotonic()

                if message and message.get("type") == "message":
                    raw_data = message["data"]
                    try:
                        payload = json.loads(raw_data)
                        msg_scope = payload.get("scope_name", "").lower()

                        # Apply scope filtering if query param given
                        if scope and msg_scope != scope.lower():
                            continue

                        # Key permission filtering: caller only receives event if at least
                        # one changed key is permitted
                        changed_keys = payload.get("changed_keys", [])
                        if not has_wildcard:
                            permitted_changed = [
                                k for k in changed_keys if k in permitted_keys
                            ]
                            if not permitted_changed:
                                continue

                        yield f"event: secret_update\ndata: {raw_data}\n\n"
                        yielded_count += 1
                        last_ping = now

                        if max_events is not None and yielded_count >= max_events:
                            break
                    except json.JSONDecodeError:
                        continue
                elif now - last_ping >= 15.0:
                    # 15s elapsed without message -> transmit heartbeat ping
                    ping_data = json.dumps({"timestamp": datetime.now(UTC).isoformat()})
                    yield f"event: ping\ndata: {ping_data}\n\n"
                    yielded_count += 1
                    last_ping = now

                    if max_events is not None and yielded_count >= max_events:
                        break
                else:
                    await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            logger.debug("SSE stream client disconnected from project {}", project_id)
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()
            await client.aclose()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
