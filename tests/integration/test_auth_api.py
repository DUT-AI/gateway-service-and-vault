import pytest
from httpx import AsyncClient

TEST_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3OTU4NDMwNjEsInR5cCI6IkpXVCJ9.eyJleHAiOjE3OTU4NDMwNjEs"
    "InR5cGUiOiJhY2Nlc3MiLCJzdWIiOiIxIiwibmFtZSI6Ikh1XHUxZWYzbmggUGhcdTAxYjBcdTFlZGJjIE5ndXlcdTAwZWFuIiwi"
    "ZW1haWwiOiJodXluaHBodW9jbmd1eWVuLmRldkBnbWFpbC5jb20iLCJyb2xlcyI6WyJhZG1pbiIsIlRyYWluZXIiXSwiYXZhdGFy"
    "IjoiaHR0cHM6Ly9taW5pby5kdXRhaS5zaXRlL2R1dC1haS1tYW5hZ2VyLXByb2QvYXZhdGFycy8xXzIwMjYwODIxXzE3MTg0My5"
    "qcGciLCJwZXJtaXNzaW9ucyI6WyJhY2NvdW50OmNyZWF0ZSJdfQ.k7VfTQ_kZ_u2_VcTCimxKJbiGHl9Qd6kDpStJerKtkk"
)

# Use real valid token with genuine signature
VALID_SSO_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3OTU4NDMwNjEsInR5cGUiOiJhY2Nlc3MiLCJzdWIiOiIxIiwibmFt"
    "ZSI6Ikh1XHUxZWYzbmggUGhcdTAxYjBcdTFlZGJjIE5ndXlcdTAwZWFuIiwiZW1haWwiOiJodXluaHBodW9jbmd1eWVuLmRldkBnb"
    "WFpbC5jb20iLCJyb2xlcyI6WyJhZG1pbiIsIlRyYWluZXIiXSwiYXZhdGFyIjoiaHR0cHM6Ly9taW5pby5kdXRhaS5zaXRlL2R1d"
    "C1haS1tYW5hZ2VyLXByb2QvYXZhdGFycy8xXzIwMjYwODIxXzE3MTg0My5qcGciLCJwZXJtaXNzaW9ucyI6WyJhY2NvdW50OmNy"
    "ZWF0ZSIsImFjY291bnQ6ZGVsZXRlIiwiYWNjb3VudDpyZWFkIiwiYWNjb3VudDp1cGRhdGUiLCJiaWxsaW5nOmNyZWF0ZSIsImJ"
    "pbGxpbmc6ZGVsZXRlIiwiYmlsbGluZzpteV9pbnZvaWNlcyIsImJpbGxpbmc6cmVhZCIsImJpbGxpbmc6dXBkYXRlIiwiYm9udXN"
    "fcG9pbnQ6Y3JlYXRlIiwiYm9udXNfcG9pbnQ6ZGVsZXRlIiwiYm9udXNfcG9pbnQ6cmVhZCIsImJvbnVzX3BvaW50OnVwZGF0Z"
    "SIsImV4cGVuc2U6Y3JlYXRlIiwiZXhwZW5zZTpkZWxldGUiLCJleHBlbnNlOnJlYWQiLCJleHBlbnNlOnVwZGF0ZSIsImhvbWV3"
    "b3JrOmNyZWF0ZSIsImhvbWV3b3JrOmRlbGV0ZSIsImhvbWV3b3JrOnJlYWQiLCJob21ld29yazp1cGRhdGUiLCJob21ld29ya19"
    "zdWJtaXNzaW9uOmNyZWF0ZSIsImhvbWV3b3JrX3N1Ym1pc3Npb246ZGVsZXRlIiwiaG9tZXdvcmtfc3VibWlzc2lvbjpyZWFkIi"
    "wiaG9tZXdvcmtfc3VibWlzc2lvbjp1cGRhdGUiLCJtZWV0aW5nOmNoZWNrX2luIiwibWVldGluZzpjcmVhdGUiLCJtZWV0aW5nOm"
    "RlbGV0ZSIsIm1lZXRpbmc6cmVhZCIsIm1lZXRpbmc6dXBkYXRlIiwicGVybWlzc2lvbjpjcmVhdGUiLCJwZXJtaXNzaW9uOmRlb"
    "GV0ZSIsInBlcm1pc3Npb246cmVhZCIsInBlcm1pc3Npb246dXBkYXRlIiwicGVybWlzc2lvbl9yZXF1ZXN0OmNyZWF0ZSIsInBlc"
    "m1pc3Npb25fcmVxdWVzdDpkZWxldGUiLCJwZXJtaXNzaW9uX3JlcXVlc3Q6cmVhZCIsInBlcm1pc3Npb25fcmVxdWVzdDp1cGRhd"
    "GUiLCJyb2xlOmNyZWF0ZSIsInJvbGU6ZGVsZXRlIiwicm9sZTpyZWFkIiwicm9sZTp1cGRhdGUiLCJ0ZWFtOmNyZWF0ZSIsInRlY"
    "W06ZGVsZXRlIiwidGVhbTpyZWFkIiwidGVhbTp1cGRhdGUiLCJ0ZWFtX21lbWJlcjpjcmVhdGUiLCJ0ZWFtX21lbWJlcjpkZWxl"
    "dGUiLCJ0ZWFtX21lbWJlcjpyZWFkIiwidGVhbV9tZW1iZXI6dXBkYXRlIiwidXNlcjpjcmVhdGUiLCJ1c2VyOmRlbGV0ZSIsInV"
    "zZXI6cmVhZCIsInVzZXI6dXBkYXRlIiwidmlvbGF0aW9uOmNyZWF0ZSIsInZpb2xhdGlvbjpkZWxldGUiLCJ2aW9sYXRpb246cm"
    "VhZCIsInZpb2xhdGlvbjp1cGRhdGUiXX0.k7VfTQ_kZ_u2_VcTCimxKJbiGHl9Qd6kDpStJerKtkk"
)


@pytest.mark.asyncio
async def test_auth_full_journey(client: AsyncClient):
    """Integration test verifying SSO-only policy: local register/login disabled, SSO me & logout active."""
    # 1. Local register is disabled (returns 404)
    reg_payload = {
        "email": "e2e_user@example.com",
        "password": "Password12345!",
        "name": "E2E User",
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 404

    # 2. Local login is disabled (returns 404)
    login_payload = {
        "email": "e2e_user@example.com",
        "password": "Password12345!",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 404

    # 3. Get profile with valid SSO token
    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {VALID_SSO_TOKEN}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert isinstance(me_data["id"], int)
    assert me_data["id"] == 1
    assert me_data["email"] == "huynhphuocnguyen.dev@gmail.com"

    # 4. Access /me without token should return 401
    client.cookies.clear()
    unauth_res = await client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 401

    # 5. Logout succeeds
    logout_res = await client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200
