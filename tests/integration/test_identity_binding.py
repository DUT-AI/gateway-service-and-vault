import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_identity_binding_full_lifecycle(client: AsyncClient):
    """Test registering clients, generating virtual keys, and verifying identity binding."""
    # 1. Create two projects: Project A and Project B
    proj_a_res = await client.post(
        "/api/v1/gateway/projects",
        json={
            "name": "Project Alpha",
            "slug": "project-alpha",
            "description": "Alpha service",
        },
    )
    assert proj_a_res.status_code == 201
    proj_a = proj_a_res.json()
    proj_a_id = proj_a["id"]

    proj_b_res = await client.post(
        "/api/v1/gateway/projects",
        json={
            "name": "Project Beta",
            "slug": "project-beta",
            "description": "Beta service",
        },
    )
    assert proj_b_res.status_code == 201
    proj_b = proj_b_res.json()
    proj_b_id = proj_b["id"]

    # 2. Register Client A (Developer Workstation) and Client B (Docker Workload)
    client_a_res = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "MacBook-Pro-Dev1",
            "client_type": "USER_DEVICE",
            "owner_id": "usr_dev_1",
        },
    )
    assert client_a_res.status_code == 201
    client_a = client_a_res.json()
    assert "cert_fingerprint" in client_a
    assert "cert_pem" in client_a

    client_b_res = await client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Docker-App-Service",
            "client_type": "APP_SERVER",
            "owner_id": "app_billing",
        },
    )
    assert client_b_res.status_code == 201
    client_b = client_b_res.json()

    # 3. Generate Virtual Access Key for Client A on Project A
    key_a_res = await client.post(
        "/api/v1/gateway/keys",
        json={"client_id": client_a["id"], "project_id": proj_a_id},
    )
    assert key_a_res.status_code == 201
    key_a = key_a_res.json()
    virtual_key_a = key_a["virtual_key"]
    assert virtual_key_a.startswith("vk_live_")

    # 4. Valid Verification: Client A calls Project A with Client A certificate
    verify_valid = await client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": virtual_key_a,
            "cert_fingerprint": client_a["cert_fingerprint"],
            "project_id": proj_a_id,
        },
    )
    assert verify_valid.status_code == 200
    assert verify_valid.json()["valid"] is True

    # 5. Attack Scenario 1: Key Replay on another machine (Client B uses Key A)
    verify_stolen_machine = await client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": virtual_key_a,
            "cert_fingerprint": client_b["cert_fingerprint"],  # Client B's certificate!
            "project_id": proj_a_id,
        },
    )
    assert verify_stolen_machine.status_code in [400, 403]
    err_json = verify_stolen_machine.json()
    assert "IdentityMismatchError" in err_json.get("code", "")

    # 6. Attack Scenario 2: Cross-project key use (Key A used to access Project B)
    verify_cross_project = await client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": virtual_key_a,
            "cert_fingerprint": client_a["cert_fingerprint"],
            "project_id": proj_b_id,  # Project B instead of Project A!
        },
    )
    assert verify_cross_project.status_code in [400, 403]
    err_json = verify_cross_project.json()
    assert "IdentityMismatchError" in err_json.get("code", "")

    # 7. Attack Scenario 3: Forged / Non-existent Key
    verify_forged_key = await client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": "vk_live_forged_key_1234567890",
            "cert_fingerprint": client_a["cert_fingerprint"],
            "project_id": proj_a_id,
        },
    )
    assert verify_forged_key.status_code in [400, 403]
