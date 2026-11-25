import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_service_scoping_enforcement_by_slug(admin_client: AsyncClient):
    """Test verifying identity binding with dynamic service_slug scoping."""
    # 1. Create a Project
    proj_res = await admin_client.post(
        "/api/v1/gateway/projects",
        json={
            "name": "Scoping Project",
            "slug": "scoping-project",
            "description": "Test dynamic service scoping",
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 2. Register Client
    client_res = await admin_client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Dev Workstation",
            "client_type": "USER_DEVICE",
            "owner_id": "dev_scope_user",
        },
    )
    assert client_res.status_code == 201
    c_data = client_res.json()
    client_id = c_data["id"]
    cert_fp = c_data["cert_fingerprint"]

    # 3. Create two Upstream Services: 'allowed-svc' and 'restricted-svc'
    svc1_res = await admin_client.post(
        "/api/v1/gateway/services",
        json={
            "name": "Allowed Service",
            "slug": "allowed-svc",
            "base_url": "https://api.allowed.com/v1",
            "auth_type": "API_KEY",
            "credential": "test_key_allowed",
        },
    )
    assert svc1_res.status_code == 201
    svc1_id = svc1_res.json()["id"]

    svc2_res = await admin_client.post(
        "/api/v1/gateway/services",
        json={
            "name": "Restricted Service",
            "slug": "restricted-svc",
            "base_url": "https://api.restricted.com/v1",
            "auth_type": "BEARER_TOKEN",
            "credential": "test_token_restricted",
        },
    )
    assert svc2_res.status_code == 201

    # 4. Bind ONLY svc1 to the Project
    bind_res = await admin_client.post(
        f"/api/v1/gateway/projects/{proj_id}/services",
        json={"service_id": svc1_id, "rate_limit_rpm": 60, "quota_daily": 1000},
    )
    assert bind_res.status_code == 201

    # 5. Generate Virtual Key for this Client and Project
    key_res = await admin_client.post(
        "/api/v1/gateway/keys",
        json={"client_id": client_id, "project_id": proj_id},
    )
    assert key_res.status_code == 201
    raw_key = key_res.json()["virtual_key"]

    # 6. Verify binding with allowed service_slug -> MUST SUCCEED (200 OK)
    ok_res = await admin_client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_key,
            "cert_fingerprint": cert_fp,
            "project_id": proj_id,
            "service_slug": "allowed-svc",
        },
    )
    assert ok_res.status_code == 200
    assert ok_res.json()["valid"] is True

    # 7. Verify binding with unallowed service_slug -> MUST FAIL (403 Forbidden)
    fail_res = await admin_client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_key,
            "cert_fingerprint": cert_fp,
            "project_id": proj_id,
            "service_slug": "restricted-svc",
        },
    )
    assert fail_res.status_code == 403
    err_body = fail_res.json()
    err_msg = err_body.get("message") or err_body.get("detail", "")
    assert "not permitted" in err_msg.lower()


@pytest.mark.asyncio
async def test_client_device_revocation_lifecycle(admin_client: AsyncClient):
    """Test revoking a client device and verifying all keys are atomically invalidated."""
    # 1. Create Project and Register Client
    proj_res = await admin_client.post(
        "/api/v1/gateway/projects",
        json={
            "name": "Revocation Test Project",
            "slug": "revocation-test-project",
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    client_res = await admin_client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Compromised Laptop",
            "client_type": "USER_DEVICE",
            "owner_id": "usr_compromised",
        },
    )
    assert client_res.status_code == 201
    c_data = client_res.json()
    client_id = c_data["id"]
    cert_fp = c_data["cert_fingerprint"]

    # 2. Generate Virtual Key
    key_res = await admin_client.post(
        "/api/v1/gateway/keys",
        json={"client_id": client_id, "project_id": proj_id},
    )
    assert key_res.status_code == 201
    raw_key = key_res.json()["virtual_key"]

    # 3. Before revocation: verify binding works
    pre_res = await admin_client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_key,
            "cert_fingerprint": cert_fp,
            "project_id": proj_id,
        },
    )
    assert pre_res.status_code == 200

    # 4. Revoke the Client Device via POST /clients/{client_id}/revoke
    revoke_res = await admin_client.post(f"/api/v1/gateway/clients/{client_id}/revoke")
    assert revoke_res.status_code == 200
    rev_data = revoke_res.json()
    assert rev_data["is_revoked"] is True
    assert rev_data["client_id"] == client_id

    # 5. After revocation: verify binding MUST FAIL (403 Forbidden)
    post_res = await admin_client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_key,
            "cert_fingerprint": cert_fp,
            "project_id": proj_id,
        },
    )
    assert post_res.status_code == 403
    post_body = post_res.json()
    post_msg = post_body.get("message") or post_body.get("detail", "")
    assert "inactive" in post_msg.lower() or "revoked" in post_msg.lower()

    # 6. Verify client listing shows is_revoked = True
    list_res = await admin_client.get("/api/v1/gateway/clients")
    assert list_res.status_code == 200
    clients = list_res.json()
    target_client = next(c for c in clients if c["id"] == client_id)
    assert target_client["is_revoked"] is True

    # 7. Revoke non-existent client -> 404
    not_found_res = await admin_client.post(
        "/api/v1/gateway/clients/01JNONEXISTENT00000000000000/revoke"
    )
    assert not_found_res.status_code == 404
