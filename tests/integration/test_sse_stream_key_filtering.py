import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.main import app
from tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_sse_stream_filters_events_by_identity_permissions():
    """Verify that an identity connected to SSE only receives secret_update events

    when an authorized secret key changes, and suppresses notifications for unauthorized keys.
    """
    transport_post = ASGITransport(app=app)
    transport_stream = ASGITransport(app=app)

    # 1. Create a project
    async with AsyncClient(
        transport=transport_post, base_url="http://test", headers=make_auth_headers()
    ) as client_post:
        proj_res = await client_post.post(
            "/api/v1/gateway/projects",
            json={"name": "Stream Filter App", "slug": "stream-filter-app"},
        )
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        # Create two secrets
        await client_post.post(
            f"/api/v1/vault/projects/{proj_id}/secrets",
            json={
                "scope_name": "common",
                "key": "DATABASE_URL",
                "value": "initial_db_url",
            },
            headers={"x-actor-id": "admin"},
        )
        await client_post.post(
            f"/api/v1/vault/projects/{proj_id}/secrets",
            json={
                "scope_name": "payment",
                "key": "STRIPE_KEY",
                "value": "initial_stripe",
            },
            headers={"x-actor-id": "admin"},
        )

        # Grant client_db access ONLY to DATABASE_URL
        grant_res = await client_post.post(
            f"/api/v1/vault/projects/{proj_id}/permissions",
            json={
                "identity_id": "client_db",
                "identity_type": "client",
                "secret_key": "DATABASE_URL",
            },
            headers={"x-actor-id": "admin"},
        )
        assert grant_res.status_code == 201

    lines: list[str] = []

    async def consume_stream():
        async with (
            AsyncClient(
                transport=transport_stream, base_url="http://test"
            ) as client_stream,
            client_stream.stream(
                "GET",
                f"/api/v1/vault/projects/{proj_id}/stream?max_events=2",
                headers={"x-identity-id": "client_db"},
            ) as response,
        ):
            assert response.status_code == 200
            async for line in response.aiter_lines():
                if line:
                    lines.append(line)

    stream_task = asyncio.create_task(consume_stream())
    await asyncio.sleep(0.3)

    async with AsyncClient(
        transport=transport_post, base_url="http://test"
    ) as client_post:
        # Update STRIPE_KEY (unauthorized for client_db) -> must NOT trigger notification
        res_stripe = await client_post.post(
            f"/api/v1/vault/projects/{proj_id}/secrets",
            json={
                "scope_name": "payment",
                "key": "STRIPE_KEY",
                "value": "updated_stripe",
            },
            headers={"x-actor-id": "admin"},
        )
        assert res_stripe.status_code == 201
        await asyncio.sleep(0.3)

        # Update DATABASE_URL (authorized for client_db) -> MUST trigger notification
        res_db = await client_post.post(
            f"/api/v1/vault/projects/{proj_id}/secrets",
            json={
                "scope_name": "common",
                "key": "DATABASE_URL",
                "value": "updated_db_url",
            },
            headers={"x-actor-id": "admin"},
        )
        assert res_db.status_code == 201

    await asyncio.wait_for(stream_task, timeout=5.0)

    joined = "\n".join(lines)
    # Connected event received
    assert "event: connected" in joined
    # secret_update for DATABASE_URL received
    assert "event: secret_update" in joined
    assert "DATABASE_URL" in joined
    # STRIPE_KEY must NOT be present in stream received by client_db
    assert "STRIPE_KEY" not in joined
