import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_audit_api_filtering_and_security_alerts(admin_client: AsyncClient):
    """Verify GET /audit-events filtering and GET /security-alerts anomaly detection."""
    # 1. Create a Project
    proj_res = await admin_client.post(
        "/api/v1/gateway/projects",
        json={
            "name": "Audit API Test Project",
            "slug": "audit-api-test-proj",
            "description": "Testing audit queries and alerts",
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 2. Register Client
    client_res = await admin_client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Audit API Client",
            "client_type": "APP_SERVER",
            "owner_id": "app_backend_service",
        },
    )
    assert client_res.status_code == 201
    c_data = client_res.json()
    client_id = c_data["id"]
    cert_fingerprint = c_data["cert_fingerprint"]

    # 3. Create Upstream Service & Bind
    svc_res = await admin_client.post(
        "/api/v1/gateway/services",
        json={
            "name": "Alert Upstream Service",
            "slug": "alert-service",
            "base_url": "http://alert-mock:8080",
            "auth_type": "BEARER_TOKEN",
            "credential": "test-key-alert",
        },
    )
    assert svc_res.status_code == 201
    svc_id = svc_res.json()["id"]

    await admin_client.post(
        f"/api/v1/gateway/projects/{proj_id}/services",
        json={"service_id": svc_id, "rate_limit_rpm": 60, "quota_daily": 100},
    )

    # 4. Generate Virtual Key
    vk_res = await admin_client.post(
        "/api/v1/gateway/keys",
        json={"client_id": client_id, "project_id": proj_id},
    )
    assert vk_res.status_code == 201
    raw_vk = vk_res.json()["virtual_key"]

    # 5. Send 1 Valid Request (ALLOW)
    allow_res = await admin_client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": cert_fingerprint,
            "project_id": proj_id,
            "service_id": svc_id,
            "service_slug": "alert-service",
            "client_ip": "10.0.0.1",
        },
    )
    assert allow_res.status_code == 200

    # 6. Send 3 Mismatched Requests (Triggering Security Alert threshold)
    wrong_fp = "aa:bb:cc:dd:ee:ff:11:22:33:44:55:66:77:88:99:00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff:00"
    for i in range(3):
        mismatch_res = await admin_client.post(
            "/api/v1/gateway/verify-binding",
            json={
                "raw_virtual_key": raw_vk,
                "cert_fingerprint": wrong_fp,
                "project_id": proj_id,
                "service_id": svc_id,
                "service_slug": "alert-service",
                "client_ip": "10.0.0.99",
            },
        )
        assert mismatch_res.status_code == 403

    # 7. Test GET /api/v1/gateway/audit-events with project_id filter
    events_res = await admin_client.get(
        f"/api/v1/gateway/audit-events?project_id={proj_id}"
    )
    assert events_res.status_code == 200
    events_data = events_res.json()
    assert events_data["total"] >= 4
    assert len(events_data["items"]) >= 4

    # Test filtering by decision=ALLOW
    allow_events_res = await admin_client.get(
        f"/api/v1/gateway/audit-events?project_id={proj_id}&decision=ALLOW"
    )
    assert allow_events_res.status_code == 200
    allow_data = allow_events_res.json()
    assert allow_data["total"] == 1
    assert allow_data["items"][0]["decision"] == "ALLOW"
    assert allow_data["items"][0]["client_type"] == "APP_SERVER"

    # Test filtering by decision=DENY and error_code=IDENTITY_MISMATCH
    deny_events_res = await admin_client.get(
        f"/api/v1/gateway/audit-events?project_id={proj_id}&decision=DENY&error_code=IDENTITY_MISMATCH"
    )
    assert deny_events_res.status_code == 200
    deny_data = deny_events_res.json()
    assert deny_data["total"] == 3
    for item in deny_data["items"]:
        assert item["decision"] == "DENY"
        assert item["error_code"] == "IDENTITY_MISMATCH"
        assert item["client_ip"] == "10.0.0.99"

    # Test pagination
    paged_res = await admin_client.get(
        f"/api/v1/gateway/audit-events?project_id={proj_id}&limit=2&offset=0"
    )
    assert paged_res.status_code == 200
    paged_data = paged_res.json()
    assert len(paged_data["items"]) == 2
    assert paged_data["limit"] == 2
    assert paged_data["offset"] == 0

    # 8. Test GET /api/v1/gateway/security-alerts
    alerts_res = await admin_client.get(
        "/api/v1/gateway/security-alerts?window_minutes=5&threshold=3"
    )
    assert alerts_res.status_code == 200
    alerts_data = alerts_res.json()
    assert alerts_data["total_active"] >= 1

    # Check alert details
    matching_alert = next(
        (a for a in alerts_data["alerts"] if a["actor_id"] == client_id),
        None,
    )
    assert matching_alert is not None
    assert matching_alert["severity"] == "HIGH"
    assert matching_alert["anomaly_type"] == "REPEATED_IDENTITY_MISMATCH"
    assert matching_alert["event_count"] >= 3
    assert matching_alert["client_ip"] == "10.0.0.99"
