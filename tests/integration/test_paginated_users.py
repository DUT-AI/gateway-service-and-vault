import pytest
from httpx import AsyncClient

from modules.identity.models.user import UserModel


@pytest.mark.asyncio
async def test_get_paginated_users_endpoint(client: AsyncClient, db_session):
    """Verify GET /api/v1/auth/users endpoint returns paginated response."""
    # Seed 5 users
    for i in range(1, 6):
        db_session.add(
            UserModel(
                email=f"list_user_{i}@example.com",
                name=f"List User {i}",
                role="user",
                status="ACTIVE",
            )
        )
    await db_session.flush()

    # Request page 1 with page_size 2
    response = await client.get("/api/v1/auth/users?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data

    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) == 2
    assert data["total"] >= 5

    # Test search query
    search_res = await client.get("/api/v1/auth/users?search=list_user_3")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert len(search_data["items"]) == 1
    assert search_data["items"][0]["email"] == "list_user_3@example.com"
