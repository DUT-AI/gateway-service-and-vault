import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_granular_key_permissions_retrieval(client: AsyncClient):
    """Verify that an identity only receives granted keys, ungranted keys are omitted,

    and direct unauthorized key requests return 403 Forbidden.
    """
    # 1. Create a project
    p_res = await client.post(
        "/api/v1/gateway/projects",
        json={"name": "Fintech Platform", "slug": "fintech-platform"},
    )
    assert p_res.status_code == 201
    proj_id = p_res.json()["id"]

    # 2. Add two secrets under different scopes
    s1_res = await client.post(
        f"/api/v1/vault/projects/{proj_id}/secrets",
        json={
            "scope_name": "common",
            "key": "DATABASE_URL",
            "value": "postgresql://dbuser:secret@postgres:5432/app",
        },
        headers={"x-actor-id": "admin"},
    )
    assert s1_res.status_code == 201

    s2_res = await client.post(
        f"/api/v1/vault/projects/{proj_id}/secrets",
        json={
            "scope_name": "payment",
            "key": "STRIPE_SECRET_KEY",
            "value": "sk_live_very_confidential_stripe_token",
        },
        headers={"x-actor-id": "admin"},
    )
    assert s2_res.status_code == 201

    # 3. Grant dev_alice access ONLY to DATABASE_URL
    grant_res = await client.post(
        f"/api/v1/vault/projects/{proj_id}/permissions",
        json={
            "identity_id": "dev_alice",
            "identity_type": "user",
            "secret_key": "DATABASE_URL",
        },
        headers={"x-actor-id": "admin"},
    )
    assert grant_res.status_code == 201
    assert grant_res.json()["secret_key"] == "DATABASE_URL"

    # 4. Identity dev_alice reads secrets -> only DATABASE_URL returned, STRIPE_SECRET_KEY omitted
    alice_res = await client.get(
        f"/api/v1/vault/projects/{proj_id}/secrets",
        headers={"x-identity-id": "dev_alice"},
    )
    assert alice_res.status_code == 200
    alice_scopes = alice_res.json()["scopes"]
    assert "common" in alice_scopes
    assert (
        alice_scopes["common"]["DATABASE_URL"]
        == "postgresql://dbuser:secret@postgres:5432/app"
    )
    # payment scope / STRIPE_SECRET_KEY must NOT be exposed
    assert "payment" not in alice_scopes
    for scope_keys in alice_scopes.values():
        assert "STRIPE_SECRET_KEY" not in scope_keys

    # 5. Identity dev_bob (zero grants) reads secrets -> returns empty scopes {}
    bob_res = await client.get(
        f"/api/v1/vault/projects/{proj_id}/secrets",
        headers={"x-identity-id": "dev_bob"},
    )
    assert bob_res.status_code == 200
    assert bob_res.json()["scopes"] == {}

    # 6. Identity dev_alice queries authorized key directly -> 200 OK
    alice_single_ok = await client.get(
        f"/api/v1/vault/projects/{proj_id}/secrets?key=DATABASE_URL",
        headers={"x-identity-id": "dev_alice"},
    )
    assert alice_single_ok.status_code == 200
    assert "DATABASE_URL" in alice_single_ok.json()["scopes"]["common"]

    # 7. Identity dev_alice queries unauthorized key directly -> 403 Forbidden
    alice_single_denied = await client.get(
        f"/api/v1/vault/projects/{proj_id}/secrets?key=STRIPE_SECRET_KEY",
        headers={"x-identity-id": "dev_alice"},
    )
    assert alice_single_denied.status_code == 403
    assert "ScopePermissionDeniedError" in alice_single_denied.json().get("code", "")
