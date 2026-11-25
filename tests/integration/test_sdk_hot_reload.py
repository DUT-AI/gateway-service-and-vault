import asyncio
import os
import time

import pytest
from dut_vault_sdk.client import VaultClient
from httpx import ASGITransport, AsyncClient

from apps.api.main import app
from tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_sdk_in_memory_hot_reload_under_5_seconds():
    """Verify SDK connects, ingests secrets into RAM, leaves zero disk artifacts, and hot-reloads < 5s."""
    transport = ASGITransport(app=app)
    project_slug = f"hotreload-{int(time.time())}"

    # 1. Create Project and Initial Secret via API
    async with AsyncClient(
        transport=transport, base_url="http://test", headers=make_auth_headers()
    ) as api_client:
        p_res = await api_client.post(
            "/api/v1/gateway/projects",
            json={"name": "Hot Reload Project", "slug": project_slug},
        )
        assert p_res.status_code == 201
        project_id = p_res.json()["id"]

        init_secret_res = await api_client.post(
            f"/api/v1/vault/projects/{project_id}/secrets",
            json={
                "scope_name": "common",
                "key": "PAYMENT_GATEWAY_KEY",
                "value": "initial_key_v1",
            },
            headers={"x-actor-id": "lead_engineer"},
        )
        assert init_secret_res.status_code == 201

        # 2. Instantiate and connect VaultClient using in-memory ASGI transports
        fetch_async_client = AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        )
        stream_async_client = AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        )
        vault_client = VaultClient(
            base_url="http://test",
            project_id=project_id,
            user_role="admin",
            scope="common",
            inject_environ=True,
            max_events=2,
            http_client=fetch_async_client,
            stream_http_client=stream_async_client,
        )

        await vault_client.connect_async(wait_for_stream=True)
        try:
            # Verify initial secret loaded in RAM
            assert vault_client.get("PAYMENT_GATEWAY_KEY") == "initial_key_v1"
            assert os.environ.get("PAYMENT_GATEWAY_KEY") == "initial_key_v1"

            # 3. Verify Zero-Disk Invariant: No plaintext .env or tmp secret files created
            assert not os.path.exists(".env.runtime")
            assert not os.path.exists(f"/tmp/vault_{project_id}.env")

            # 4. Trigger Secret Update on Control Plane
            start_time = time.time()
            update_res = await api_client.post(
                f"/api/v1/vault/projects/{project_id}/secrets",
                json={
                    "scope_name": "common",
                    "key": "PAYMENT_GATEWAY_KEY",
                    "value": "rotated_secret_key_v2",
                },
                headers={"x-actor-id": "security_officer"},
            )
            assert update_res.status_code == 201

            # 5. Assert RAM hot-reloads value in < 5 seconds
            updated = False
            elapsed = 0.0
            while time.time() - start_time < 5.0:
                val = vault_client.get("PAYMENT_GATEWAY_KEY")
                if val == "rotated_secret_key_v2":
                    elapsed = time.time() - start_time
                    updated = True
                    break
                await asyncio.sleep(0.05)

            assert updated is True, (
                "RAM did not update to rotated secret within 5 seconds!"
            )
            assert elapsed < 5.0
            assert os.environ.get("PAYMENT_GATEWAY_KEY") == "rotated_secret_key_v2"
        finally:
            await vault_client.disconnect_async()
            await fetch_async_client.aclose()
            await stream_async_client.aclose()
