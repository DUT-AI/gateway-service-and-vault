import pytest
from httpx import AsyncClient

from tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_regular_dev_device_registration_and_project_binding(
    client: AsyncClient, admin_client: AsyncClient
):
    """Verify Tier 3 device self-registration, Project Developer binding, and read-only Virtual Key viewing."""
    # Setup: Admin creates Project X and assigns Project Developer (id=10) and Regular Dev A (id=20).
    # Regular Dev B (id=21) is NOT a member of Project X.
    proj_res = await admin_client.post(
        "/api/v1/gateway/projects",
        json={"name": "Device Binding Project", "slug": "device-binding-proj"},
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    members_res = await admin_client.post(
        f"/api/v1/gateway/projects/{project_id}/members",
        json={"user_ids": [10, 20]},
    )
    assert members_res.status_code == 201

    proj_dev_headers = make_auth_headers(
        user_id=10, roles=["Project Developer"], email="projdev@dutai.io.vn"
    )
    dev_a_headers = make_auth_headers(
        user_id=20, roles=["Trainer"], email="deva@dutai.io.vn"
    )
    dev_b_headers = make_auth_headers(
        user_id=21, roles=["Content"], email="devb@dutai.io.vn"
    )

    # 1. Tier 3 (Regular Dev A) can self-register USER_DEVICE (201)
    dev_a_pc_res = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Dev A MacBook",
            "client_type": "USER_DEVICE",
            "owner_id": "999",  # Spoof attempt; server enforces owner_id="20"
            "validity_days": 30,
        },
        headers=dev_a_headers,
    )
    assert dev_a_pc_res.status_code == 201
    assert dev_a_pc_res.json()["owner_id"] == "20"
    assert dev_a_pc_res.json()["client_type"] == "USER_DEVICE"
    dev_a_pc_id = dev_a_pc_res.json()["id"]

    # 2. Tier 3 (Regular Dev A) CANNOT register APP_SERVER (403 Forbidden)
    dev_a_srv_res = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Dev A Illegal Server",
            "client_type": "APP_SERVER",
            "validity_days": 30,
        },
        headers=dev_a_headers,
    )
    assert dev_a_srv_res.status_code == 403

    # Regular Dev B (non-member of Project X) registers their own USER_DEVICE
    dev_b_pc_res = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Dev B Laptop",
            "client_type": "USER_DEVICE",
            "validity_days": 30,
        },
        headers=dev_b_headers,
    )
    assert dev_b_pc_res.status_code == 201
    dev_b_pc_id = dev_b_pc_res.json()["id"]

    # 3. Tier 3 cross-user client revocation is rejected (403 Forbidden)
    cross_revoke_res = await client.post(
        f"/api/v1/gateway/clients/{dev_b_pc_id}/revoke",
        headers=dev_a_headers,
    )
    assert cross_revoke_res.status_code == 403

    # 4. Project Developer registers their own APP_SERVER and queries available-clients for Project X
    proj_dev_srv_res = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Project X Staging Server",
            "client_type": "APP_SERVER",
            "validity_days": 90,
        },
        headers=proj_dev_headers,
    )
    assert proj_dev_srv_res.status_code == 201
    proj_dev_srv_id = proj_dev_srv_res.json()["id"]

    avail_res = await client.get(
        f"/api/v1/gateway/projects/{project_id}/available-clients",
        headers=proj_dev_headers,
    )
    assert avail_res.status_code == 200
    avail_ids = {c["id"] for c in avail_res.json()}
    # Sees Project X members' devices (10 and 20), NOT non-member Dev B (21)
    assert dev_a_pc_id in avail_ids
    assert proj_dev_srv_id in avail_ids
    assert dev_b_pc_id not in avail_ids

    # Regular Dev A cannot call available-clients (403 Forbidden)
    assert (
        await client.get(
            f"/api/v1/gateway/projects/{project_id}/available-clients",
            headers=dev_a_headers,
        )
    ).status_code == 403

    # 5. Project Developer generates Virtual Keys for Dev A's device and their own server
    key_for_dev_a_res = await client.post(
        "/api/v1/gateway/keys",
        json={"project_id": project_id, "client_id": dev_a_pc_id},
        headers=proj_dev_headers,
    )
    assert key_for_dev_a_res.status_code == 201
    key_for_dev_a_id = key_for_dev_a_res.json()["id"]

    key_for_proj_dev_res = await client.post(
        "/api/v1/gateway/keys",
        json={"project_id": project_id, "client_id": proj_dev_srv_id},
        headers=proj_dev_headers,
    )
    assert key_for_proj_dev_res.status_code == 201
    key_for_proj_dev_id = key_for_proj_dev_res.json()["id"]

    # 6. Regular Dev A reads GET /projects/{id}/keys -> sees ONLY key bound to own device
    dev_a_keys_res = await client.get(
        f"/api/v1/gateway/projects/{project_id}/keys",
        headers=dev_a_headers,
    )
    assert dev_a_keys_res.status_code == 200
    dev_a_key_ids = {k["id"] for k in dev_a_keys_res.json()}
    assert key_for_dev_a_id in dev_a_key_ids
    assert key_for_proj_dev_id not in dev_a_key_ids

    # Project Developer sees ALL keys in Project X
    proj_dev_keys_res = await client.get(
        f"/api/v1/gateway/projects/{project_id}/keys",
        headers=proj_dev_headers,
    )
    assert proj_dev_keys_res.status_code == 200
    proj_dev_key_ids = {k["id"] for k in proj_dev_keys_res.json()}
    assert {key_for_dev_a_id, key_for_proj_dev_id}.issubset(proj_dev_key_ids)

    # 7. Regular Dev A CANNOT generate or revoke Virtual Keys (403 Forbidden)
    assert (
        await client.post(
            "/api/v1/gateway/keys",
            json={"project_id": project_id, "client_id": dev_a_pc_id},
            headers=dev_a_headers,
        )
    ).status_code == 403
    assert (
        await client.post(
            f"/api/v1/gateway/keys/{key_for_dev_a_id}/revoke",
            headers=dev_a_headers,
        )
    ).status_code == 403

    # 8. Regular Dev A can revoke their own device on /clients
    self_revoke_res = await client.post(
        f"/api/v1/gateway/clients/{dev_a_pc_id}/revoke",
        headers=dev_a_headers,
    )
    assert self_revoke_res.status_code == 200
    assert self_revoke_res.json()["is_revoked"] is True
