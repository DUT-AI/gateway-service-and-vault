import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.gateway.models.audit import AuditEventModel


@pytest.mark.asyncio
async def test_audit_event_recording_on_gateway_verification(
    client: AsyncClient, db_session: AsyncSession
):
    """Verify that VerifyIdentityBindingUseCase persists immutable audit logs for ALLOW and DENY decisions."""
    # 1. Create a Project
    proj_res = await client.post(
        "/api/v1/gateway/projects",
        json={
            "name": "Audit Test Project",
            "slug": "audit-test-proj",
            "description": "Project for testing audit events",
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 2. Register Client
    client_res = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Audit Test Client",
            "client_type": "USER_DEVICE",
            "owner_id": "auditor_user",
        },
    )
    assert client_res.status_code == 201
    c_data = client_res.json()
    client_id = c_data["id"]
    cert_fingerprint = c_data["cert_fingerprint"]

    # 3. Create Upstream Service & Bind to Project with quota_daily = 2
    svc_res = await client.post(
        "/api/v1/gateway/services",
        json={
            "name": "Audit Upstream Service",
            "slug": "audit-llm-service",
            "base_url": "http://mock-service:8080",
            "auth_type": "BEARER_TOKEN",
            "credential": "test-key-audit",
        },
    )
    assert svc_res.status_code == 201
    svc_id = svc_res.json()["id"]

    bind_res = await client.post(
        f"/api/v1/gateway/projects/{proj_id}/services",
        json={
            "service_id": svc_id,
            "rate_limit_rpm": 60,
            "quota_daily": 2,
        },
    )
    assert bind_res.status_code == 201

    # 4. Generate Virtual Key
    vk_res = await client.post(
        "/api/v1/gateway/keys",
        json={"client_id": client_id, "project_id": proj_id},
    )
    assert vk_res.status_code == 201
    raw_vk = vk_res.json()["virtual_key"]

    # 5. Call verify-binding with VALID credentials -> ALLOW
    allow_res = await client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": cert_fingerprint,
            "project_id": proj_id,
            "service_id": svc_id,
            "service_slug": "audit-llm-service",
            "client_ip": "192.168.1.100",
        },
    )
    assert allow_res.status_code == 200

    # 6. Call verify-binding with WRONG fingerprint -> DENY (IDENTITY_MISMATCH)
    mismatch_res = await client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": "00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff",
            "project_id": proj_id,
            "service_id": svc_id,
            "service_slug": "audit-llm-service",
            "client_ip": "192.168.1.101",
        },
    )
    assert mismatch_res.status_code == 403

    # 7. Consume remaining quota call
    allow_res_2 = await client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": cert_fingerprint,
            "project_id": proj_id,
            "service_id": svc_id,
            "service_slug": "audit-llm-service",
            "client_ip": "192.168.1.100",
        },
    )
    assert allow_res_2.status_code == 200

    # 8. Call 3rd time -> Exceed quota -> DENY (DAILY_QUOTA_EXCEEDED)
    quota_exceeded_res = await client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": cert_fingerprint,
            "project_id": proj_id,
            "service_id": svc_id,
            "service_slug": "audit-llm-service",
            "client_ip": "192.168.1.100",
        },
    )
    assert quota_exceeded_res.status_code == 429

    # 9. Verify recorded audit events in database
    stmt = (
        select(AuditEventModel)
        .where(AuditEventModel.project_id == proj_id)
        .order_by(AuditEventModel.timestamp.asc())
    )
    result = await db_session.execute(stmt)
    audit_events = result.scalars().all()

    assert len(audit_events) == 4

    # Check Event 1: ALLOW
    assert audit_events[0].decision == "ALLOW"
    assert audit_events[0].error_code is None
    assert audit_events[0].action == "GATEWAY_ACCESS"
    assert audit_events[0].actor_id == client_id
    assert audit_events[0].client_type == "USER_DEVICE"
    assert audit_events[0].client_ip == "192.168.1.100"

    # Check Event 2: DENY (IDENTITY_MISMATCH)
    assert audit_events[1].decision == "DENY"
    assert audit_events[1].error_code == "IDENTITY_MISMATCH"
    assert audit_events[1].client_ip == "192.168.1.101"

    # Check Event 3: ALLOW
    assert audit_events[2].decision == "ALLOW"
    assert audit_events[2].error_code is None

    # Check Event 4: DENY (DAILY_QUOTA_EXCEEDED)
    assert audit_events[3].decision == "DENY"
    assert audit_events[3].error_code == "DAILY_QUOTA_EXCEEDED"
