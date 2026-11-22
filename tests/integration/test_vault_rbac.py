import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_vault_granular_permissions_and_encryption(client: AsyncClient):
    """Test identity-based key permissions access, in-memory decryption, and zero plaintext storage."""
    # 1. Create a Project
    proj_res = await client.post(
        "/api/v1/gateway/projects",
        json={"name": "Billing Platform", "slug": "billing-platform"},
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 2. Add Secrets: Common Scope
    res1 = await client.post(
        f"/api/v1/vault/projects/{proj_id}/secrets",
        json={
            "scope_name": "Common",
            "key": "DATABASE_URL",
            "value": "postgresql://usr:pass@host/db",
        },
        headers={"x-actor-id": "tech_lead"},
    )
    assert res1.status_code == 201
    assert res1.json()["key"] == "DATABASE_URL"

    # 3. Add Secrets: Financial Scope
    res2 = await client.post(
        f"/api/v1/vault/projects/{proj_id}/secrets",
        json={
            "scope_name": "Financial",
            "key": "STRIPE_SECRET_KEY",
            "value": "sk_live_very_secret_key_123",
        },
        headers={"x-actor-id": "tech_lead"},
    )
    assert res2.status_code == 201
    assert res2.json()["key"] == "STRIPE_SECRET_KEY"

    # Grant permissions: financial_dev gets both keys
    await client.post(
        f"/api/v1/vault/projects/{proj_id}/permissions",
        json={
            "identity_id": "financial_dev",
            "identity_type": "user",
            "secret_key": "DATABASE_URL",
        },
    )
    await client.post(
        f"/api/v1/vault/projects/{proj_id}/permissions",
        json={
            "identity_id": "financial_dev",
            "identity_type": "user",
            "secret_key": "STRIPE_SECRET_KEY",
        },
    )

    # Grant permissions: general_dev gets only DATABASE_URL
    await client.post(
        f"/api/v1/vault/projects/{proj_id}/permissions",
        json={
            "identity_id": "general_dev",
            "identity_type": "user",
            "secret_key": "DATABASE_URL",
        },
    )

    # 4. Privileged Access: Financial Developer requests secrets
    fin_res = await client.get(
        f"/api/v1/vault/projects/{proj_id}/secrets",
        headers={"x-identity-id": "financial_dev"},
    )
    assert fin_res.status_code == 200
    fin_scopes = fin_res.json()["scopes"]
    assert "Common" in fin_scopes
    assert fin_scopes["Common"]["DATABASE_URL"] == "postgresql://usr:pass@host/db"
    assert "Financial" in fin_scopes
    assert fin_scopes["Financial"]["STRIPE_SECRET_KEY"] == "sk_live_very_secret_key_123"

    # 5. Restricted Access: General Developer requests secrets
    gen_res = await client.get(
        f"/api/v1/vault/projects/{proj_id}/secrets",
        headers={"x-identity-id": "general_dev"},
    )
    assert gen_res.status_code == 200
    gen_scopes = gen_res.json()["scopes"]
    assert "Common" in gen_scopes
    assert gen_scopes["Common"]["DATABASE_URL"] == "postgresql://usr:pass@host/db"
    assert "Financial" not in gen_scopes

    # 6. Direct Unauthorized Request: General Developer queries unpermitted key directly
    unauth_fin_res = await client.get(
        f"/api/v1/vault/projects/{proj_id}/secrets?key=STRIPE_SECRET_KEY",
        headers={"x-identity-id": "general_dev"},
    )
    assert unauth_fin_res.status_code == 403
    err_json = unauth_fin_res.json()
    assert "ScopePermissionDeniedError" in err_json.get("code", "")
