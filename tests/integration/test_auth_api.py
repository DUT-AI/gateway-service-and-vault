import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_full_journey(client: AsyncClient):
    """Integration test for register, login, and get_current_user."""
    # 1. Register user
    reg_payload = {
        "email": "e2e_user@example.com",
        "password": "Password12345!",
        "name": "E2E User",
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["email"] == "e2e_user@example.com"
    assert user_data["name"] == "E2E User"
    assert "id" in user_data

    # 2. Duplicate registration should return 409 Conflict
    dup_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 409
    dup_data = dup_res.json()
    assert dup_data["code"] == "UserAlreadyExistsError"

    # 3. Login with credentials
    login_payload = {
        "email": "e2e_user@example.com",
        "password": "Password12345!",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 4. Get current user profile with token
    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "e2e_user@example.com"
    assert me_data["name"] == "E2E User"

    # 5. Access /me without token should return 401
    unauth_res = await client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 401
