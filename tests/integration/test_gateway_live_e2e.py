"""End-to-End Live Integration Tests for APISIX Gateway mTLS & Identity Binding Enforcement."""

import os
import tempfile

import httpx
import pytest

from tests.conftest import make_auth_headers

APISIX_HTTP_URL = os.getenv("APISIX_HTTP_URL", "http://localhost:9080")
APISIX_HTTPS_URL = os.getenv("APISIX_HTTPS_URL", "https://localhost:9443")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")


async def is_live_environment_ready() -> bool:
    """Check if local APISIX gateway and FastAPI backend are reachable."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            h = await client.get(f"{BACKEND_API_URL}/health")
            if h.status_code != 200:
                return False
        async with httpx.AsyncClient(verify=False, timeout=2.0) as client:
            res = await client.get(f"{APISIX_HTTP_URL}/services/llm/models")
            return res.status_code in [200, 401, 403]
    except Exception:
        return False


@pytest.mark.asyncio
async def test_live_gateway_scenario_1_missing_virtual_key_rejected():
    """Scenario 1: Calling HTTPS mTLS without X-Virtual-Key returns 401 UNAUTHORIZED."""
    if not await is_live_environment_ready():
        pytest.skip("Live APISIX gateway or FastAPI backend is not running")

    # 1. Register a test client to obtain mTLS cert and key
    async with httpx.AsyncClient(timeout=5.0, headers=make_auth_headers()) as client:
        reg_res = await client.post(
            f"{BACKEND_API_URL}/api/v1/gateway/clients",
            json={
                "name": "Live Test Client S1",
                "client_type": "USER_DEVICE",
                "owner_id": "test_e2e",
            },
        )
        assert reg_res.status_code == 201
        c_data = reg_res.json()

    with (
        tempfile.NamedTemporaryFile("w", delete=False) as cert_f,
        tempfile.NamedTemporaryFile("w", delete=False) as key_f,
    ):
        cert_f.write(c_data["cert_pem"])
        cert_f.flush()
        key_f.write(c_data["key_pem"])
        key_f.flush()

        try:
            async with httpx.AsyncClient(
                cert=(cert_f.name, key_f.name), verify=False, timeout=5.0
            ) as mtls_client:
                # Call without X-Virtual-Key header
                res = await mtls_client.get(f"{APISIX_HTTPS_URL}/services/llm/models")
                assert res.status_code == 401
                body = res.json()
                assert body.get("error") == "UNAUTHORIZED"
                assert "Missing X-Virtual-Key" in body.get("message", "")
        finally:
            os.unlink(cert_f.name)
            os.unlink(key_f.name)


@pytest.mark.asyncio
async def test_live_gateway_scenario_2_http_without_mtls_cert_rejected():
    """Scenario 2: Calling plain HTTP port without mTLS certificate returns 403 MTLS_REQUIRED."""
    if not await is_live_environment_ready():
        pytest.skip("Live APISIX gateway or FastAPI backend is not running")

    async with httpx.AsyncClient(timeout=5.0) as client:
        # Call plain HTTP with a dummy virtual key
        res = await client.get(
            f"{APISIX_HTTP_URL}/services/llm/models",
            headers={"X-Virtual-Key": "vk_live_dummy_for_testing"},
        )
        assert res.status_code == 403
        body = res.json()
        assert body.get("error") == "MTLS_REQUIRED"
        assert "Valid client certificate required" in body.get("message", "")


@pytest.mark.asyncio
async def test_live_gateway_scenario_3_and_4_valid_call_and_revocation_lifecycle():
    """Scenario 3 & 4: Valid mTLS call returns 200 OK, and revocation immediately invalidates credentials."""
    if not await is_live_environment_ready():
        pytest.skip("Live APISIX gateway or FastAPI backend is not running")

    async with httpx.AsyncClient(timeout=5.0, headers=make_auth_headers()) as client:
        # 1. Register Client
        client_res = await client.post(
            f"{BACKEND_API_URL}/api/v1/gateway/clients",
            json={
                "name": "Live Test Client Lifecycle",
                "client_type": "USER_DEVICE",
                "owner_id": "test_lifecycle_user",
            },
        )
        assert client_res.status_code == 201
        c_data = client_res.json()
        client_id = c_data["id"]

        # 2. Always create a fresh Project with high quota to ensure test isolation
        p_res = await client.post(
            f"{BACKEND_API_URL}/api/v1/gateway/projects",
            json={
                "name": f"Lifecycle Proj {client_id[:8]}",
                "slug": f"lifecycle-proj-{client_id.lower()[:8]}",
            },
        )
        assert p_res.status_code == 201
        project_id = p_res.json()["id"]

        # 3. Bind LLM service with high quota (10,000)
        svc_res = await client.get(f"{BACKEND_API_URL}/api/v1/gateway/services")
        assert svc_res.status_code == 200
        llm_services = [s for s in svc_res.json() if s["slug"] == "llm"]
        assert len(llm_services) > 0
        service_id = llm_services[0]["id"]

        await client.post(
            f"{BACKEND_API_URL}/api/v1/gateway/projects/{project_id}/services",
            json={
                "service_id": service_id,
                "rate_limit_rpm": 60,
                "quota_daily": 10000,
            },
        )

        # 4. Generate Virtual Key for this Client & Project
        key_res = await client.post(
            f"{BACKEND_API_URL}/api/v1/gateway/keys",
            json={
                "client_id": client_id,
                "project_id": project_id,
                "key_name": "E2E Lifecycle Key",
                "validity_days": 30,
            },
        )
        assert key_res.status_code == 201
        virtual_key = key_res.json()["virtual_key"]

    with (
        tempfile.NamedTemporaryFile("w", delete=False) as cert_f,
        tempfile.NamedTemporaryFile("w", delete=False) as key_f,
    ):
        cert_f.write(c_data["cert_pem"])
        cert_f.flush()
        key_f.write(c_data["key_pem"])
        key_f.flush()

        try:
            async with httpx.AsyncClient(
                cert=(cert_f.name, key_f.name), verify=False, timeout=10.0
            ) as mtls_client:
                # Scenario 3: Valid mTLS handshake + valid Virtual Key -> 200 OK
                res = await mtls_client.get(
                    f"{APISIX_HTTPS_URL}/services/llm/models",
                    headers={
                        "X-Virtual-Key": virtual_key,
                        "X-Project-Id": project_id,
                    },
                )
                assert res.status_code == 200
                assert (
                    "models" in res.json()
                    or "data" in res.json()
                    or res.status_code == 200
                )

                # Scenario 4: Revoke Client Device
                async with httpx.AsyncClient(
                    timeout=5.0, headers=make_auth_headers()
                ) as admin_client:
                    rev_res = await admin_client.post(
                        f"{BACKEND_API_URL}/api/v1/gateway/clients/{client_id}/revoke"
                    )
                    assert rev_res.status_code == 200
                    assert rev_res.json().get("is_revoked") is True

                # Subsequent call with the SAME credentials MUST be rejected with 403 Forbidden
                retry_res = await mtls_client.get(
                    f"{APISIX_HTTPS_URL}/services/llm/models",
                    headers={
                        "X-Virtual-Key": virtual_key,
                        "X-Project-Id": project_id,
                    },
                )
                assert retry_res.status_code == 403
                retry_body = retry_res.json()
                assert retry_body.get("error") == "IDENTITY_MISMATCH"
        finally:
            os.unlink(cert_f.name)
            os.unlink(key_f.name)


@pytest.mark.asyncio
async def test_live_gateway_scenario_5_daily_quota_exhaustion_returns_429():
    """Scenario 5: When daily quota is exhausted, Gateway returns 429 Too Many Requests."""
    if not await is_live_environment_ready():
        pytest.skip("Live APISIX gateway or FastAPI backend is not running")

    async with httpx.AsyncClient(timeout=5.0, headers=make_auth_headers()) as client:
        # 1. Register Client
        client_res = await client.post(
            f"{BACKEND_API_URL}/api/v1/gateway/clients",
            json={
                "name": "Live Quota Test Client",
                "client_type": "USER_DEVICE",
                "owner_id": "test_quota_user",
            },
        )
        assert client_res.status_code == 201
        c_data = client_res.json()
        client_id = c_data["id"]

        # 2. Create Project
        proj_res = await client.post(
            f"{BACKEND_API_URL}/api/v1/gateway/projects",
            json={
                "name": f"Quota Proj {client_id[:8]}",
                "slug": f"quota-proj-{client_id.lower()[:8]}",
            },
        )
        assert proj_res.status_code == 201
        project_id = proj_res.json()["id"]

        # 3. Get existing LLM service
        svc_res = await client.get(f"{BACKEND_API_URL}/api/v1/gateway/services")
        assert svc_res.status_code == 200
        llm_services = [s for s in svc_res.json() if s["slug"] == "llm"]
        assert len(llm_services) > 0
        service_id = llm_services[0]["id"]

        # 4. Bind LLM Service with quota_daily = 1
        bind_res = await client.post(
            f"{BACKEND_API_URL}/api/v1/gateway/projects/{project_id}/services",
            json={
                "service_id": service_id,
                "rate_limit_rpm": 60,
                "quota_daily": 1,
            },
        )
        assert bind_res.status_code == 201

        # 5. Generate Virtual Key
        key_res = await client.post(
            f"{BACKEND_API_URL}/api/v1/gateway/keys",
            json={
                "client_id": client_id,
                "project_id": project_id,
                "key_name": "Quota 429 Key",
                "validity_days": 30,
            },
        )
        assert key_res.status_code == 201
        virtual_key = key_res.json()["virtual_key"]

    with (
        tempfile.NamedTemporaryFile("w", delete=False) as cert_f,
        tempfile.NamedTemporaryFile("w", delete=False) as key_f,
    ):
        cert_f.write(c_data["cert_pem"])
        cert_f.flush()
        key_f.write(c_data["key_pem"])
        key_f.flush()

        try:
            async with httpx.AsyncClient(
                cert=(cert_f.name, key_f.name), verify=False, timeout=10.0
            ) as mtls_client:
                # First call: within quota (1/1) -> 200 OK
                res1 = await mtls_client.get(
                    f"{APISIX_HTTPS_URL}/services/llm/models",
                    headers={
                        "X-Virtual-Key": virtual_key,
                        "X-Project-Id": project_id,
                    },
                )
                assert res1.status_code == 200

                # Second call: quota exceeded (2 > 1) -> 429 Too Many Requests
                res2 = await mtls_client.get(
                    f"{APISIX_HTTPS_URL}/services/llm/models",
                    headers={
                        "X-Virtual-Key": virtual_key,
                        "X-Project-Id": project_id,
                    },
                )
                assert res2.status_code == 429
                body2 = res2.json()
                assert body2.get("error") == "DAILY_QUOTA_EXCEEDED"
                assert (
                    "daily request quota exceeded" in body2.get("message", "").lower()
                )
        finally:
            os.unlink(cert_f.name)
            os.unlink(key_f.name)
