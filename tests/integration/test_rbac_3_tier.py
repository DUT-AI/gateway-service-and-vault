import pytest
from httpx import AsyncClient

from tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_standardized_3_tier_rbac_and_project_membership(
    client: AsyncClient, admin_client: AsyncClient
):
    """End-to-end verification of 3-tier RBAC (ADMIN, PROJECT_DEVELOPER, OTHER) and Project Membership."""
    # 0. Unauthenticated requests to Gateway management endpoints must return 401
    unauth_res = await client.get("/api/v1/gateway/projects")
    assert unauth_res.status_code == 401

    # 1. ADMIN creates Project A and Project B, plus secrets in Project A
    proj_a_res = await admin_client.post(
        "/api/v1/gateway/projects",
        json={"name": "RBAC Project A", "slug": "rbac-project-a"},
    )
    assert proj_a_res.status_code == 201
    proj_a_id = proj_a_res.json()["id"]

    proj_b_res = await admin_client.post(
        "/api/v1/gateway/projects",
        json={"name": "RBAC Project B", "slug": "rbac-project-b"},
    )
    assert proj_b_res.status_code == 201
    proj_b_id = proj_b_res.json()["id"]

    sec_admin_res = await admin_client.post(
        f"/api/v1/vault/projects/{proj_a_id}/secrets",
        json={
            "scope_name": "Common",
            "key": "ADMIN_SECRET",
            "value": "top_secret_admin_val",
        },
    )
    assert sec_admin_res.status_code == 201

    # Admin assigns Developer (user_id=10) and Trainer (user_id=20) to Project A ONLY in a single batch call
    add_members_res = await admin_client.post(
        f"/api/v1/gateway/projects/{proj_a_id}/members",
        json={"user_ids": [10, 20]},
    )
    assert add_members_res.status_code == 201
    assert {m["user_id"] for m in add_members_res.json()} == {10, 20}

    # 2. PROJECT DEVELOPER (user_id=10, role="Project Developer")
    dev_headers = make_auth_headers(
        user_id=10, roles=["Project Developer"], email="dev@dutai.io.vn"
    )

    # Sees ONLY Project A
    dev_projects = (
        await client.get("/api/v1/gateway/projects", headers=dev_headers)
    ).json()
    dev_proj_ids = {p["id"] for p in dev_projects}
    assert proj_a_id in dev_proj_ids
    assert proj_b_id not in dev_proj_ids

    # Accessing unassigned Project B -> 403 Forbidden
    dev_b_res = await client.get(
        f"/api/v1/gateway/projects/{proj_b_id}", headers=dev_headers
    )
    assert dev_b_res.status_code == 403

    # Cannot create projects or manage members -> 403 Forbidden
    assert (
        await client.post(
            "/api/v1/gateway/projects",
            json={"name": "Dev Unauthorized", "slug": "dev-unauth"},
            headers=dev_headers,
        )
    ).status_code == 403
    assert (
        await client.post(
            f"/api/v1/gateway/projects/{proj_a_id}/members",
            json={"user_ids": [99]},
            headers=dev_headers,
        )
    ).status_code == 403

    # Can read ALL secrets in assigned Project A without explicit key_permissions
    dev_secrets_res = await client.get(
        f"/api/v1/vault/projects/{proj_a_id}/secrets", headers=dev_headers
    )
    assert dev_secrets_res.status_code == 200
    assert (
        dev_secrets_res.json()["scopes"]["Common"]["ADMIN_SECRET"]
        == "top_secret_admin_val"
    )

    # Can register client & generate virtual key for assigned Project A
    dev_client_res = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Dev Machine",
            "client_type": "APP_SERVER",
            "owner_id": "10",
        },
        headers=dev_headers,
    )
    assert dev_client_res.status_code == 201
    dev_key_res = await client.post(
        "/api/v1/gateway/keys",
        json={
            "client_id": dev_client_res.json()["id"],
            "project_id": proj_a_id,
        },
        headers=dev_headers,
    )
    assert dev_key_res.status_code == 201

    # 3. OTHER ROLES (user_id=20, role="Trainer")
    trainer_headers = make_auth_headers(
        user_id=20, roles=["Trainer"], email="trainer@dutai.io.vn"
    )

    # Sees ONLY Project A and can view Project A details
    trainer_projects = (
        await client.get("/api/v1/gateway/projects", headers=trainer_headers)
    ).json()
    trainer_proj_ids = {p["id"] for p in trainer_projects}
    assert proj_a_id in trainer_proj_ids
    assert proj_b_id not in trainer_proj_ids
    assert (
        await client.get(
            f"/api/v1/gateway/projects/{proj_a_id}", headers=trainer_headers
        )
    ).status_code == 200
    assert (
        await client.get(
            f"/api/v1/gateway/projects/{proj_b_id}", headers=trainer_headers
        )
    ).status_code == 403

    # Cannot see ADMIN_SECRET initially (even with spoofed X-Identity-Id / X-User-Role headers!)
    spoofed_headers = {
        **trainer_headers,
        "X-Identity-Id": "admin",
        "X-User-Role": "admin",
    }
    trainer_sec_res = await client.get(
        f"/api/v1/vault/projects/{proj_a_id}/secrets", headers=spoofed_headers
    )
    assert trainer_sec_res.status_code == 200
    assert trainer_sec_res.json()["scopes"] == {}

    # Trainer creates TRAINER_KEY -> immediately visible to Trainer, ADMIN_SECRET still hidden
    trainer_create_sec = await client.post(
        f"/api/v1/vault/projects/{proj_a_id}/secrets",
        json={
            "scope_name": "Common",
            "key": "TRAINER_KEY",
            "value": "trainer_own_val",
        },
        headers=trainer_headers,
    )
    assert trainer_create_sec.status_code == 201

    trainer_sec_after = (
        await client.get(
            f"/api/v1/vault/projects/{proj_a_id}/secrets", headers=trainer_headers
        )
    ).json()["scopes"]
    assert trainer_sec_after["Common"]["TRAINER_KEY"] == "trainer_own_val"
    assert "ADMIN_SECRET" not in trainer_sec_after["Common"]

    # Admin grants ADMIN_SECRET to Trainer -> now Trainer sees both
    grant_res = await admin_client.post(
        f"/api/v1/vault/projects/{proj_a_id}/permissions",
        json={
            "identity_id": "20",
            "identity_type": "user",
            "secret_key": "ADMIN_SECRET",
        },
    )
    assert grant_res.status_code == 201

    trainer_sec_granted = (
        await client.get(
            f"/api/v1/vault/projects/{proj_a_id}/secrets", headers=trainer_headers
        )
    ).json()["scopes"]
    assert trainer_sec_granted["Common"]["ADMIN_SECRET"] == "top_secret_admin_val"
    assert trainer_sec_granted["Common"]["TRAINER_KEY"] == "trainer_own_val"

    # Trainer cannot create clients, keys, or grant permissions -> 403 Forbidden
    assert (
        await client.post(
            "/api/v1/gateway/clients",
            json={"name": "Nope", "client_type": "USER_DEVICE", "owner_id": "20"},
            headers=trainer_headers,
        )
    ).status_code == 403
    assert (
        await client.post(
            f"/api/v1/vault/projects/{proj_a_id}/permissions",
            json={"identity_id": "20", "identity_type": "user", "secret_key": "X"},
            headers=trainer_headers,
        )
    ).status_code == 403
