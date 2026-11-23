import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_project_service_binding_and_quota_lifecycle(client: AsyncClient):
    """Test binding an upstream service to a project, updating quota, listing, and unbinding."""
    # 1. Create a project
    proj_res = await client.post(
        "/api/v1/gateway/projects",
        json={
            "name": "Finance Core Platform",
            "slug": "finance-core-platform",
            "description": "Core payment integration hub",
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 2. Register an upstream service
    svc_res = await client.post(
        "/api/v1/gateway/services",
        json={
            "name": "VNPay Sandbox Gateway",
            "slug": "vnpay-sandbox-gw",
            "base_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
            "auth_type": "BEARER_TOKEN",
            "credential": "vnpay_secret_checksum_hash_key",
            "timeout_seconds": 30,
        },
    )
    assert svc_res.status_code == 201
    svc_id = svc_res.json()["id"]

    # 3. Initially, no services are bound to the project
    list_initial = await client.get(f"/api/v1/gateway/projects/{proj_id}/services")
    assert list_initial.status_code == 200
    assert list_initial.json() == []

    # 4. Bind the service to the project with quota
    bind_res = await client.post(
        f"/api/v1/gateway/projects/{proj_id}/services",
        json={
            "service_id": svc_id,
            "rate_limit_rpm": 120,
            "quota_daily": 50000,
        },
    )
    assert bind_res.status_code == 201
    bound_data = bind_res.json()
    assert bound_data["service_id"] == svc_id
    assert bound_data["service_name"] == "VNPay Sandbox Gateway"
    assert bound_data["rate_limit_rpm"] == 120
    assert bound_data["quota_daily"] == 50000
    assert bound_data["is_quota_active"] is True

    # 5. List allowed services for project
    list_res = await client.get(f"/api/v1/gateway/projects/{proj_id}/services")
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) == 1
    assert items[0]["service_id"] == svc_id
    assert items[0]["rate_limit_rpm"] == 120

    # 6. Duplicate binding attempt must return 409 Conflict
    dup_res = await client.post(
        f"/api/v1/gateway/projects/{proj_id}/services",
        json={
            "service_id": svc_id,
            "rate_limit_rpm": 60,
            "quota_daily": 10000,
        },
    )
    assert dup_res.status_code == 409
    assert "already bound" in dup_res.json()["detail"].lower()

    # 7. Update quota policy for the binding
    update_res = await client.put(
        f"/api/v1/gateway/projects/{proj_id}/services/{svc_id}/quota",
        json={
            "rate_limit_rpm": 300,
            "quota_daily": 100000,
        },
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["rate_limit_rpm"] == 300
    assert updated_data["quota_daily"] == 100000

    # 8. Unbind service from project
    unbind_res = await client.delete(
        f"/api/v1/gateway/projects/{proj_id}/services/{svc_id}"
    )
    assert unbind_res.status_code == 204

    # 9. List services again -> now empty
    list_after = await client.get(f"/api/v1/gateway/projects/{proj_id}/services")
    assert list_after.status_code == 200
    assert list_after.json() == []

    # 10. Unbinding an already unbound service returns 404
    unbind_404 = await client.delete(
        f"/api/v1/gateway/projects/{proj_id}/services/{svc_id}"
    )
    assert unbind_404.status_code == 404


@pytest.mark.asyncio
async def test_zero_trust_gateway_enforces_project_service_allowlist(
    client: AsyncClient,
):
    """Verify that a project's virtual key can only access allowed upstream services."""
    # 1. Create Project Alpha
    proj_res = await client.post(
        "/api/v1/gateway/projects",
        json={
            "name": "Project Alpha Security",
            "slug": "project-alpha-security",
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 2. Register Upstream S1 (OpenAI) and Upstream S2 (Secret Banking)
    s1_res = await client.post(
        "/api/v1/gateway/services",
        json={
            "name": "OpenAI Public Models",
            "slug": "openai-public-models",
            "base_url": "https://api.openai.com/v1",
            "auth_type": "BEARER_TOKEN",
            "credential": "sk-proj-openai-allowed",
            "timeout_seconds": 30,
        },
    )
    s1_id = s1_res.json()["id"]

    s2_res = await client.post(
        "/api/v1/gateway/services",
        json={
            "name": "Secret Core Banking API",
            "slug": "secret-core-banking-api",
            "base_url": "https://internal-bank.local/api",
            "auth_type": "API_KEY",
            "credential": "bank_super_secret_key",
            "timeout_seconds": 15,
        },
    )
    s2_id = s2_res.json()["id"]

    # 3. Bind ONLY S1 (OpenAI) to Project Alpha
    bind_res = await client.post(
        f"/api/v1/gateway/projects/{proj_id}/services",
        json={
            "service_id": s1_id,
            "rate_limit_rpm": 60,
            "quota_daily": 10000,
        },
    )
    assert bind_res.status_code == 201

    # 4. Register mTLS client and issue Virtual Key for Project Alpha
    client_res = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Secure-Edge-Worker",
            "client_type": "APP_SERVER",
            "owner_id": "99",
            "validity_days": 30,
        },
    )
    assert client_res.status_code == 201
    client_data = client_res.json()
    client_id = client_data["id"]
    cert_fingerprint = client_data["cert_fingerprint"]

    key_res = await client.post(
        "/api/v1/gateway/keys",
        json={
            "client_id": client_id,
            "project_id": proj_id,
        },
    )
    assert key_res.status_code == 201
    virtual_key = key_res.json()["virtual_key"]

    # 5. Gateway Check 1: Target S1 (bound service) -> MUST be allowed
    check_s1 = await client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": virtual_key,
            "cert_fingerprint": cert_fingerprint,
            "project_id": proj_id,
            "service_id": s1_id,
        },
    )
    assert check_s1.status_code == 200
    assert check_s1.json()["valid"] is True

    # 6. Gateway Check 2: Target S2 (unbound service) -> MUST return 403 Forbidden
    check_s2 = await client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": virtual_key,
            "cert_fingerprint": cert_fingerprint,
            "project_id": proj_id,
            "service_id": s2_id,
        },
    )
    assert check_s2.status_code == 403
    error_msg = check_s2.json().get("message") or check_s2.json().get("detail", "")
    assert "not permitted" in error_msg.lower()
