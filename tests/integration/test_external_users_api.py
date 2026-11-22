import pytest
from httpx import AsyncClient

TEST_TOKEN = (
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
async def test_get_user_options_endpoint(client: AsyncClient):
    """Verify GET /api/v1/users/options returns list of users with integer IDs."""
    res = await client.get(
        "/api/v1/users/options",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    if items:
        first = items[0]
        assert isinstance(first["id"], int)
        assert "name" in first
        assert "email" in first


@pytest.mark.asyncio
async def test_get_user_by_id_endpoint_success(client: AsyncClient):
    """Verify GET /api/v1/users/1 returns detail profile for ID 1 with strict integer ID."""
    res = await client.get(
        "/api/v1/users/1",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )
    assert res.status_code == 200
    user = res.json()
    assert isinstance(user["id"], int)
    assert user["id"] == 1
    assert user["email"] == "huynhphuocnguyen.dev@gmail.com"


@pytest.mark.asyncio
async def test_get_user_by_id_rejects_non_integer_id(client: AsyncClient):
    """Verify GET /api/v1/users/abc is strictly rejected with HTTP 422 Unprocessable Entity."""
    res = await client.get(
        "/api/v1/users/abc",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )
    assert res.status_code == 422
