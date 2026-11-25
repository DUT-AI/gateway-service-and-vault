import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.main import app
from tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_sse_stream_receives_connected_and_secret_update():
    transport1 = ASGITransport(app=app)
    transport2 = ASGITransport(app=app)

    # 1. Create a Project first to satisfy foreign key constraint
    async with AsyncClient(
        transport=transport2, base_url="http://test", headers=make_auth_headers()
    ) as client_post:
        proj_res = await client_post.post(
            "/api/v1/gateway/projects",
            json={"name": "Streaming App", "slug": "streaming-app"},
        )
        assert proj_res.status_code == 201
        project_id = proj_res.json()["id"]

        # Pre-create initial secret
        res = await client_post.post(
            f"/api/v1/vault/projects/{project_id}/secrets",
            json={
                "scope_name": "common",
                "key": "INIT_KEY",
                "value": "initial_value",
            },
            headers={"x-actor-id": "test_actor"},
        )
        assert res.status_code == 201

    lines: list[str] = []

    async def consume_stream():
        async with (
            AsyncClient(transport=transport1, base_url="http://test") as client_stream,
            client_stream.stream(
                "GET",
                f"/api/v1/vault/projects/{project_id}/stream?max_events=2",
                headers={"x-identity-id": "admin"},
            ) as response,
        ):
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]
            async for line in response.aiter_lines():
                if line:
                    lines.append(line)

    stream_task = asyncio.create_task(consume_stream())

    # Wait for connected event to arrive
    await asyncio.sleep(0.3)

    # Trigger update via separate client
    async with AsyncClient(transport=transport2, base_url="http://test") as client_post:
        update_res = await client_post.post(
            f"/api/v1/vault/projects/{project_id}/secrets",
            json={
                "scope_name": "common",
                "key": "UPDATED_KEY",
                "value": "new_value",
            },
            headers={"x-actor-id": "updater"},
        )
        assert update_res.status_code == 201

    await asyncio.wait_for(stream_task, timeout=5.0)

    joined = "\n".join(lines)
    assert "event: connected" in joined
    assert "event: secret_update" in joined
    assert "UPDATED_KEY" in joined


@pytest.mark.asyncio
async def test_sse_stream_max_events_closes_connection():
    transport = ASGITransport(app=app)
    lines: list[str] = []
    async with (
        AsyncClient(transport=transport, base_url="http://test") as client,
        client.stream(
            "GET",
            "/api/v1/vault/projects/non_existent_proj/stream?max_events=1",
            headers={"x-identity-id": "admin"},
        ) as response,
    ):
        assert response.status_code == 200
        async for line in response.aiter_lines():
            if line:
                lines.append(line)

    joined = "\n".join(lines)
    assert "event: connected" in joined
