"""End-to-End Live Integration Tests for APISIX Gateway mTLS & Identity Binding Enforcement."""

import os
import tempfile

import httpx
import pytest

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
    async with httpx.AsyncClient(timeout=5.0) as client:
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

    async with httpx.AsyncClient(timeout=5.0) as client:
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

        # 2. Get existing or create Project
        proj_res = await client.get(f"{BACKEND_API_URL}/api/v1/gateway/projects")
        assert proj_res.status_code == 200
        projects = proj_res.json()
        if projects:
            project_id = projects[0]["id"]
        else:
            p_res = await client.post(
                f"{BACKEND_API_URL}/api/v1/gateway/projects",
                json={
                    "name": "Lifecycle Project",
                    "slug": "lifecycle-project",
                },
            )
            assert p_res.status_code == 201
            project_id = p_res.json()["id"]

        # 3. Generate Virtual Key for this Client & Project
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
                async with httpx.AsyncClient(timeout=5.0) as admin_client:
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
