import pytest
from httpx import AsyncClient

from tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_delete_vault_secret_and_3_tier_rbac(
    client: AsyncClient, admin_client: AsyncClient
):
    """Verify DELETE /vault/projects/{id}/secrets across ADMIN, PROJECT_DEVELOPER, and OTHER."""
    proj_a = await admin_client.post(
        "/api/v1/gateway/projects",
        json={"name": "Vault Delete A", "slug": "vault-delete-a"},
    )
    assert proj_a.status_code == 201
    proj_a_id = proj_a.json()["id"]

    proj_b = await admin_client.post(
        "/api/v1/gateway/projects",
        json={"name": "Vault Delete B", "slug": "vault-delete-b"},
    )
    assert proj_b.status_code == 201
    proj_b_id = proj_b.json()["id"]

    # Assign Project Developer (id=10) and Regular Dev (id=20) to Project A only
    add_res = await admin_client.post(
        f"/api/v1/gateway/projects/{proj_a_id}/members",
        json={"user_ids": [10, 20]},
    )
    assert add_res.status_code == 201

    dev_headers = make_auth_headers(
        user_id=10, roles=["Project Developer"], email="dev@dutai.io.vn"
    )
    other_headers = make_auth_headers(
        user_id=20, roles=["Trainer"], email="trainer@dutai.io.vn"
    )

    # Admin creates ADMIN_KEY and DEV_TARGET_KEY in Project A, and B_KEY in Project B
    for proj_id, key_name in [
        (proj_a_id, "ADMIN_KEY"),
        (proj_a_id, "DEV_TARGET_KEY"),
        (proj_b_id, "B_KEY"),
    ]:
        res = await admin_client.post(
            f"/api/v1/vault/projects/{proj_id}/secrets",
            json={"scope_name": "Common", "key": key_name, "value": "val_123"},
        )
        assert res.status_code == 201

    # 1. RoleTier.OTHER cannot delete ADMIN_KEY (403)
    other_deny = await client.delete(
        f"/api/v1/vault/projects/{proj_a_id}/secrets",
        params={"scope_name": "Common", "key": "ADMIN_KEY"},
        headers=other_headers,
    )
    assert other_deny.status_code == 403

    # 2. RoleTier.OTHER creates OWN_KEY and can delete it (200)
    other_create = await client.post(
        f"/api/v1/vault/projects/{proj_a_id}/secrets",
        json={"scope_name": "Common", "key": "OWN_KEY", "value": "mine"},
        headers=other_headers,
    )
    assert other_create.status_code == 201

    other_del = await client.delete(
        f"/api/v1/vault/projects/{proj_a_id}/secrets",
        params={"scope_name": "Common", "key": "OWN_KEY"},
        headers=other_headers,
    )
    assert other_del.status_code == 200
    assert other_del.json()["key"] == "OWN_KEY"

    # 3. Assigned Project Developer can delete DEV_TARGET_KEY in Project A (200)
    dev_del = await client.delete(
        f"/api/v1/vault/projects/{proj_a_id}/secrets",
        params={"scope_name": "Common", "key": "DEV_TARGET_KEY"},
        headers=dev_headers,
    )
    assert dev_del.status_code == 200

    # Unassigned Project Developer cannot delete B_KEY in Project B (403)
    dev_deny_b = await client.delete(
        f"/api/v1/vault/projects/{proj_b_id}/secrets",
        params={"scope_name": "Common", "key": "B_KEY"},
        headers=dev_headers,
    )
    assert dev_deny_b.status_code == 403

    # 4. Admin can delete ADMIN_KEY (200), and deleting missing key returns 404
    admin_del = await admin_client.delete(
        f"/api/v1/vault/projects/{proj_a_id}/secrets",
        params={"scope_name": "Common", "key": "ADMIN_KEY"},
    )
    assert admin_del.status_code == 200

    missing_del = await admin_client.delete(
        f"/api/v1/vault/projects/{proj_a_id}/secrets",
        params={"scope_name": "Common", "key": "ADMIN_KEY"},
    )
    assert missing_del.status_code == 404

    # Verify Project A Common scope is now empty
    get_res = await admin_client.get(f"/api/v1/vault/projects/{proj_a_id}/secrets")
    assert get_res.status_code == 200
    assert get_res.json()["scopes"].get("Common", {}) == {}
