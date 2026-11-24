import asyncio
import json
import time
from datetime import UTC, datetime
from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import StreamingResponse
from loguru import logger

from apps.api.routers.vault.auth_helpers import resolve_caller_identity
from core.config import redis_settings
from core.security.deps import get_optional_user_payload
from modules.vault.services.broadcaster import RedisVaultBroadcaster
from modules.vault.use_cases import ListIdentityPermissionsUseCase

router = APIRouter()


@router.get(
    "/projects/{project_id}/stream",
    summary="Server-Sent Events stream for dynamic secret configuration updates",
)
@inject
async def stream_project_secrets(
    project_id: str,
    permissions_use_case: FromDishka[ListIdentityPermissionsUseCase],
    scope: str | None = Query(default=None),
    identity_id: str | None = Query(default=None),
    max_events: int | None = Query(
        default=None,
        description="Max events to yield before closing stream (useful for testing)",
    ),
    user_payload: Annotated[dict | None, Depends(get_optional_user_payload)] = None,
    x_identity_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
) -> StreamingResponse:
    """Stream real-time secret update events filtered by caller key permissions."""
    caller_id = resolve_caller_identity(
        user_payload,
        x_identity_id=x_identity_id,
        x_user_role=x_user_role,
        identity_query_param=identity_id,
    )
    permitted_keys = set(
        await permissions_use_case.execute(project_id=project_id, identity_id=caller_id)
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
            logger.debug(f"SSE stream client disconnected from project {project_id}")
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
