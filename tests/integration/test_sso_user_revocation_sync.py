import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sso_user_revocation_sync(client: AsyncClient):
    """Verify cascade revocation of registered clients and virtual keys upon SSO user deactivation."""
    owner_user_id = 9876
    owner_id_str = str(owner_user_id)

    # 1. Create a Project
    proj_res = await client.post(
        "/api/v1/gateway/projects",
        json={
            "name": "SSO Revocation Test Project",
            "slug": "sso-revoc-test-proj",
            "description": "Testing cascade revocation on SSO user deactivation",
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 2. Register Client owned by SSO user
    client_res = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Employee Work Laptop",
            "client_type": "USER_DEVICE",
            "owner_id": owner_id_str,
        },
    )
    assert client_res.status_code == 201
    client_data = client_res.json()
    client_id = client_data["id"]
    cert_fp = client_data["cert_fingerprint"]

    # 3. Create Upstream Service & Bind
    svc_res = await client.post(
        "/api/v1/gateway/services",
        json={
            "name": "SSO Upstream Service",
            "slug": "sso-service",
            "base_url": "http://sso-mock:8080",
            "auth_type": "BEARER_TOKEN",
            "credential": "test-key-sso",
        },
    )
    assert svc_res.status_code == 201
    svc_id = svc_res.json()["id"]

    bind_res = await client.post(
        f"/api/v1/gateway/projects/{proj_id}/services",
        json={"service_id": svc_id, "rate_limit_rpm": 60, "quota_daily": 100},
    )
    assert bind_res.status_code == 201

    # 4. Generate Virtual Key for Client
    vk_res = await client.post(
        "/api/v1/gateway/keys",
        json={"client_id": client_id, "project_id": proj_id},
    )
    assert vk_res.status_code == 201
    raw_vk = vk_res.json()["virtual_key"]

    # 5. Verify Gateway access works prior to deactivation
    verify_before = await client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": cert_fp,
            "project_id": proj_id,
            "service_slug": "sso-service",
            "client_ip": "10.0.0.1",
        },
    )
    assert verify_before.status_code == 200
    assert verify_before.json()["valid"] is True

    # 6. Trigger SSO User Revocation Sync
    sync_res = await client.post(
        f"/api/v1/identity/users/{owner_user_id}/sync-revocation"
    )
    assert sync_res.status_code == 200
    sync_data = sync_res.json()
    assert sync_data["user_id"] == owner_user_id
    assert sync_data["revoked_clients_count"] == 1
    assert sync_data["total_clients_found"] == 1

    # 7. Verify Client status is marked revoked
    clients_res = await client.get("/api/v1/gateway/clients")
    assert clients_res.status_code == 200
    our_client = next((c for c in clients_res.json() if c["id"] == client_id), None)
    assert our_client is not None
    assert our_client["is_revoked"] is True

    # 8. Verify Virtual Key is marked REVOKED
    keys_res = await client.get(f"/api/v1/gateway/projects/{proj_id}/keys")
    assert keys_res.status_code == 200
    our_key = next((k for k in keys_res.json() if k["client_id"] == client_id), None)
    assert our_key is not None
    assert our_key["status"] == "REVOKED"

    # 9. Verify subsequent Gateway access fails closed with HTTP 403 CLIENT_REVOKED
    verify_after = await client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": cert_fp,
            "project_id": proj_id,
            "service_slug": "sso-service",
            "client_ip": "10.0.0.1",
        },
    )
    assert verify_after.status_code == 403
    err_body = verify_after.json()
    assert (
        "revoked" in err_body["message"].lower()
        or err_body["code"] == "IdentityMismatchError"
    )

    # 10. Verify Audit Event logged SSO_USER_REVOKED and subsequent DENY
    audit_res = await client.get(
        "/api/v1/gateway/audit-events",
        params={"actor_id": owner_id_str},
    )
    assert audit_res.status_code == 200
    events = audit_res.json()["items"]
    assert any(e["action"] == "SSO_USER_REVOKED" for e in events)
