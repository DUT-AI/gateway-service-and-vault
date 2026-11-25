import pytest
from httpx import AsyncClient

from tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_client_ownership_scoping_and_self_issued_enforcement(
    client: AsyncClient, admin_client: AsyncClient
):
    """Verify mTLS client self-issued ownership, Developer isolation, and Admin governance."""
    dev_a_headers = make_auth_headers(
        user_id=10, roles=["Project Developer"], email="deva@dutai.io.vn"
    )
    dev_b_headers = make_auth_headers(
        user_id=11, roles=["Project Developer"], email="devb@dutai.io.vn"
    )

    # 1. Dev A registers both USER_DEVICE and APP_SERVER, attempting to spoof owner_id="1"
    dev_a_pc = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Dev A Laptop",
            "client_type": "USER_DEVICE",
            "owner_id": "1",  # Spoof attempt
            "validity_days": 30,
        },
        headers=dev_a_headers,
    )
    assert dev_a_pc.status_code == 201
    assert dev_a_pc.json()["owner_id"] == "10"  # Locked to Dev A's SSO user_id
    dev_a_pc_id = dev_a_pc.json()["id"]

    dev_a_srv = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Dev A Worker Server",
            "client_type": "APP_SERVER",
            "validity_days": 90,
        },
        headers=dev_a_headers,
    )
    assert dev_a_srv.status_code == 201
    assert dev_a_srv.json()["owner_id"] == "10"
    dev_a_srv_id = dev_a_srv.json()["id"]

    # 2. Dev B registers their own USER_DEVICE
    dev_b_pc = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Dev B Laptop",
            "client_type": "USER_DEVICE",
            "validity_days": 30,
        },
        headers=dev_b_headers,
    )
    assert dev_b_pc.status_code == 201
    assert dev_b_pc.json()["owner_id"] == "11"
    dev_b_pc_id = dev_b_pc.json()["id"]

    # 3. GET /clients isolation: Dev A sees only own, Dev B sees only own, Admin sees all
    dev_a_list = (
        await client.get("/api/v1/gateway/clients", headers=dev_a_headers)
    ).json()
    dev_a_ids = {c["id"] for c in dev_a_list}
    assert dev_a_pc_id in dev_a_ids
    assert dev_a_srv_id in dev_a_ids
    assert dev_b_pc_id not in dev_a_ids

    dev_b_list = (
        await client.get("/api/v1/gateway/clients", headers=dev_b_headers)
    ).json()
    dev_b_ids = {c["id"] for c in dev_b_list}
    assert dev_b_pc_id in dev_b_ids
    assert dev_a_pc_id not in dev_b_ids

    admin_list = (await admin_client.get("/api/v1/gateway/clients")).json()
    admin_ids = {c["id"] for c in admin_list}
    assert {dev_a_pc_id, dev_a_srv_id, dev_b_pc_id}.issubset(admin_ids)

    # 4. Cross-user revocation is rejected with 403 Forbidden
    cross_revoke = await client.post(
        f"/api/v1/gateway/clients/{dev_a_pc_id}/revoke",
        headers=dev_b_headers,
    )
    assert cross_revoke.status_code == 403

    # 5. Admin can revoke Dev A's device; Dev B can revoke their own device
    admin_revoke = await admin_client.post(
        f"/api/v1/gateway/clients/{dev_a_pc_id}/revoke"
    )
    assert admin_revoke.status_code == 200
    assert admin_revoke.json()["is_revoked"] is True

    self_revoke = await client.post(
        f"/api/v1/gateway/clients/{dev_b_pc_id}/revoke",
        headers=dev_b_headers,
    )
    assert self_revoke.status_code == 200
    assert self_revoke.json()["is_revoked"] is True
