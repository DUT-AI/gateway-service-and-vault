import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_gateway_projects_crud(admin_client: AsyncClient):
    """Test listing and retrieving projects."""
    # 1. Create a project
    create_res = await admin_client.post(
        "/api/v1/gateway/projects",
        json={
            "name": "E-Commerce Gateway",
            "slug": "e-commerce-gw",
            "description": "Gateway for store services",
        },
    )
    assert create_res.status_code == 201
    project_data = create_res.json()
    project_id = project_data["id"]

    # 2. List projects
    list_res = await admin_client.get("/api/v1/gateway/projects")
    assert list_res.status_code == 200
    projects = list_res.json()
    assert isinstance(projects, list)
    assert any(p["id"] == project_id for p in projects)

    # 3. Get single project
    get_res = await admin_client.get(f"/api/v1/gateway/projects/{project_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "E-Commerce Gateway"

    # 4. Get non-existent project returns 404
    non_existent = await admin_client.get("/api/v1/gateway/projects/non_existent_999")
    assert non_existent.status_code == 404


@pytest.mark.asyncio
async def test_gateway_clients_listing(admin_client: AsyncClient):
    """Test listing registered mTLS clients."""
    # 1. Register a client
    reg_res = await admin_client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Dev Laptop MacBook Pro",
            "client_type": "USER_DEVICE",
            "owner_id": "1",
            "validity_days": 30,
        },
    )
    assert reg_res.status_code == 201
    client_id = reg_res.json()["id"]

    # 2. List clients
    list_res = await admin_client.get("/api/v1/gateway/clients")
    assert list_res.status_code == 200
    clients = list_res.json()
    assert isinstance(clients, list)
    assert any(c["id"] == client_id for c in clients)


@pytest.mark.asyncio
async def test_gateway_virtual_keys_and_revoke(admin_client: AsyncClient):
    """Test generating, listing, and revoking virtual access keys."""
    # Create project & client
    p_res = await admin_client.post(
        "/api/v1/gateway/projects",
        json={"name": "Billing Service", "slug": "billing-srv"},
    )
    project_id = p_res.json()["id"]

    c_res = await admin_client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Billing Worker",
            "client_type": "APP_SERVER",
            "owner_id": "billing",
        },
    )
    client_id = c_res.json()["id"]

    # Generate key
    key_res = await admin_client.post(
        "/api/v1/gateway/keys",
        json={"project_id": project_id, "client_id": client_id},
    )
    assert key_res.status_code == 201
    key_id = key_res.json()["id"]

    # List keys for project
    list_res = await admin_client.get(f"/api/v1/gateway/projects/{project_id}/keys")
    assert list_res.status_code == 200
    keys = list_res.json()
    assert len(keys) == 1
    assert keys[0]["id"] == key_id
    assert keys[0]["status"] == "ACTIVE"

    # Revoke key
    revoke_res = await admin_client.post(f"/api/v1/gateway/keys/{key_id}/revoke")
    assert revoke_res.status_code == 200

    # Verify status changed to REVOKED
    list_res2 = await admin_client.get(f"/api/v1/gateway/projects/{project_id}/keys")
    assert list_res2.json()[0]["status"] == "REVOKED"


@pytest.mark.asyncio
async def test_upstream_services_crud(admin_client: AsyncClient):
    """Test creating and listing upstream services."""
    # 1. Create upstream service
    create_res = await admin_client.post(
        "/api/v1/gateway/services",
        json={
            "name": "OpenAI LLM Gateway",
            "slug": "openai-llm",
            "base_url": "https://api.openai.com/v1",
            "auth_type": "BEARER_TOKEN",
            "credential": "sk-real-mock-secret",
            "timeout_seconds": 45,
        },
    )
    assert create_res.status_code == 201
    svc_id = create_res.json()["id"]

    # 2. List services
    list_res = await admin_client.get("/api/v1/gateway/services")
    assert list_res.status_code == 200
    services = list_res.json()
    assert any(s["id"] == svc_id for s in services)


@pytest.mark.asyncio
async def test_vault_list_scopes(admin_client: AsyncClient):
    """Test listing secret scopes in a project."""
    # 1. Create project
    p_res = await admin_client.post(
        "/api/v1/gateway/projects",
        json={"name": "Scope Test Project", "slug": "scope-test-proj"},
    )
    project_id = p_res.json()["id"]

    # 2. Add secret into a scope
    await admin_client.post(
        f"/api/v1/vault/projects/{project_id}/secrets",
        json={
            "scope_name": "Database",
            "key": "DB_URL",
            "value": "postgres://localhost/db",
        },
    )
    await admin_client.post(
        f"/api/v1/vault/projects/{project_id}/secrets",
        json={"scope_name": "Payment", "key": "STRIPE_KEY", "value": "sk_test_123"},
    )

    # 3. List scopes
    scopes_res = await admin_client.get(f"/api/v1/vault/projects/{project_id}/scopes")
    assert scopes_res.status_code == 200
    scopes = scopes_res.json()
    scope_names = {s["name"] for s in scopes}
    assert "Database" in scope_names
    assert "Payment" in scope_names
