import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_gateway_fail_closed_on_invalid_bindings(admin_client: AsyncClient):
    """Verify that Gateway strictly fails closed (HTTP 403) for any unverified request."""
    # 1. Missing / Non-existent Virtual Key
    res_unknown_key = await admin_client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": "vkey_nonexistent_1234567890abcdef",
            "cert_fingerprint": "fake_fingerprint_sha256",
            "project_id": "proj_unknown",
            "service_slug": "svc_unknown",
            "client_ip": "192.168.1.1",
        },
    )
    assert res_unknown_key.status_code == 403
    assert res_unknown_key.json()["code"] == "IdentityMismatchError"

    # 2. Setup legitimate client, project, service, and key
    proj_res = await admin_client.post(
        "/api/v1/gateway/projects",
        json={
            "name": "Fail Closed Test Project",
            "slug": "fail-closed-proj",
            "description": "Testing fail-closed invariants",
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    client_res = await admin_client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Legitimate Client",
            "client_type": "USER_DEVICE",
            "owner_id": "legit_user_1",
        },
    )
    assert client_res.status_code == 201
    client_data = client_res.json()
    client_id = client_data["id"]
    valid_fp = client_data["cert_fingerprint"]

    svc_res = await admin_client.post(
        "/api/v1/gateway/services",
        json={
            "name": "Fail-Closed Target Service",
            "slug": "fail-closed-svc",
            "base_url": "http://mock-service:8080",
            "auth_type": "BEARER_TOKEN",
            "credential": "fc-secret-key",
        },
    )
    assert svc_res.status_code == 201
    svc_id = svc_res.json()["id"]

    await admin_client.post(
        f"/api/v1/gateway/projects/{proj_id}/services",
        json={"service_id": svc_id, "rate_limit_rpm": 60, "quota_daily": 100},
    )

    vk_res = await admin_client.post(
        "/api/v1/gateway/keys",
        json={"client_id": client_id, "project_id": proj_id},
    )
    assert vk_res.status_code == 201
    raw_vk = vk_res.json()["virtual_key"]

    # 3. Valid key with mismatched certificate fingerprint -> 403 IDENTITY_MISMATCH
    res_mismatched_cert = await admin_client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": "attacker_stolen_cert_fingerprint_hash",
            "project_id": proj_id,
            "service_slug": "fail-closed-svc",
            "client_ip": "10.0.0.99",
        },
    )
    assert res_mismatched_cert.status_code == 403
    assert res_mismatched_cert.json()["code"] == "IdentityMismatchError"

    # 4. Valid key with unbound service -> 403 SERVICE_NOT_ALLOWED
    res_unbound_service = await admin_client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": valid_fp,
            "project_id": proj_id,
            "service_slug": "unauthorized-secret-finance-svc",
            "client_ip": "10.0.0.99",
        },
    )
    assert res_unbound_service.status_code == 403
    assert res_unbound_service.json()["code"] == "ServiceNotPermittedError"

    # 5. Revoked client -> 403 CLIENT_REVOKED
    revoke_client_res = await admin_client.post(
        f"/api/v1/gateway/clients/{client_id}/revoke"
    )
    assert revoke_client_res.status_code == 200

    res_revoked = await admin_client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": valid_fp,
            "project_id": proj_id,
            "service_slug": "fail-closed-svc",
            "client_ip": "10.0.0.99",
        },
    )
    assert res_revoked.status_code == 403
    assert res_revoked.json()["code"] == "IdentityMismatchError"
    msg = res_revoked.json()["message"].lower()
    assert "revoked" in msg or "inactive" in msg or "invalid" in msg
