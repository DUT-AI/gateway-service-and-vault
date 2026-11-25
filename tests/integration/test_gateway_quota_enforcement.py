import pytest
from httpx import AsyncClient

from modules.gateway.domain.interfaces import IQuotaUsageTracker


class InMemoryQuotaTracker(IQuotaUsageTracker):
    """In-memory quota tracker for test assertions."""

    def __init__(self) -> None:
        self.counters: dict[str, int] = {}

    async def get_usage(self, project_id: str, service_id: str) -> int:
        return self.counters.get(f"{project_id}:{service_id}", 0)

    async def increment_and_check(
        self, project_id: str, service_id: str, quota_daily: int
    ) -> tuple[int, bool]:
        key = f"{project_id}:{service_id}"
        val = self.counters.get(key, 0) + 1
        self.counters[key] = val
        return val, val <= quota_daily


@pytest.mark.asyncio
async def test_daily_quota_enforcement_and_usage_api(admin_client: AsyncClient):
    """Verify daily quota limit rejection (429) and real-time usage querying."""
    # 1. Create a Project
    proj_res = await admin_client.post(
        "/api/v1/gateway/projects",
        json={
            "name": "Quota Test Project",
            "slug": "quota-test-proj",
            "description": "Test daily quota enforcement",
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 2. Register Client
    client_res = await admin_client.post(
        "/api/v1/gateway/clients",
        json={
            "name": "Quota Client",
            "client_type": "USER_DEVICE",
            "owner_id": "test_quota_owner",
        },
    )
    assert client_res.status_code == 201
    c_data = client_res.json()
    client_id = c_data["id"]
    cert_fp = c_data["cert_fingerprint"]

    # 3. Create an Upstream Service
    svc_res = await admin_client.post(
        "/api/v1/gateway/services",
        json={
            "name": "LLM Quota Service",
            "slug": "llm-quota",
            "base_url": "https://api.openai.com/v1",
            "auth_type": "BEARER_TOKEN",
            "credential": "test_token_quota",
        },
    )
    assert svc_res.status_code == 201
    svc_id = svc_res.json()["id"]

    # 4. Bind Service to Project with daily quota = 2
    bind_res = await admin_client.post(
        f"/api/v1/gateway/projects/{proj_id}/services",
        json={"service_id": svc_id, "rate_limit_rpm": 60, "quota_daily": 2},
    )
    assert bind_res.status_code == 201

    # 5. Generate Virtual Key
    key_res = await admin_client.post(
        "/api/v1/gateway/keys",
        json={"client_id": client_id, "project_id": proj_id},
    )
    assert key_res.status_code == 201
    raw_vk = key_res.json()["virtual_key"]

    # 6. First Call -> 200 OK (usage = 1/2)
    verify1 = await admin_client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": cert_fp,
            "project_id": proj_id,
            "service_slug": "llm-quota",
        },
    )
    assert verify1.status_code == 200

    # 7. Check usage API
    usage_res1 = await admin_client.get(
        f"/api/v1/gateway/projects/{proj_id}/services/{svc_id}/usage"
    )
    assert usage_res1.status_code == 200
    u1 = usage_res1.json()
    assert u1["quota_daily"] == 2
    assert u1["usage_today"] >= 1
    assert u1["is_exhausted"] is False

    # 8. Check enriched allowed services list
    list_res = await admin_client.get(f"/api/v1/gateway/projects/{proj_id}/services")
    assert list_res.status_code == 200
    services = list_res.json()
    assert len(services) == 1
    assert services[0]["usage_today"] >= 1
    assert "usage_percentage" in services[0]

    # 9. Second Call -> 200 OK (usage = 2/2)
    verify2 = await admin_client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": cert_fp,
            "project_id": proj_id,
            "service_slug": "llm-quota",
        },
    )
    assert verify2.status_code == 200

    # 10. Third Call -> MUST be rejected with 429 DailyQuotaExceededError
    verify3 = await admin_client.post(
        "/api/v1/gateway/verify-binding",
        json={
            "raw_virtual_key": raw_vk,
            "cert_fingerprint": cert_fp,
            "project_id": proj_id,
            "service_slug": "llm-quota",
        },
    )
    assert verify3.status_code == 429
    v3_body = verify3.json()
    assert v3_body.get("code") == "DailyQuotaExceededError"
    assert "Daily request quota exceeded" in v3_body.get("message", "")
