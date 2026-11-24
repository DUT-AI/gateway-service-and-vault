import httpx
import pytest

from core.config import apisix_settings
from modules.gateway.client.apisix_client import ApisixAdminClient


@pytest.mark.asyncio
async def test_apisix_control_plane_route_cors_payload():
    """Verify that ApisixAdminClient configures cors plugin on control plane route."""
    client = ApisixAdminClient()
    result = await client.sync_control_plane_route()

    assert "value" in result
    route_value = result["value"]
    assert "plugins" in route_value
    assert "cors" in route_value["plugins"]

    cors_config = route_value["plugins"]["cors"]
    assert "http://localhost:3000" in cors_config["allow_origins"]
    assert cors_config["allow_credential"] is True
    assert "Authorization" in cors_config["allow_headers"]
    assert "OPTIONS" in cors_config["allow_methods"]


@pytest.mark.asyncio
async def test_apisix_gateway_cors_preflight_live():
    """Verify that APISIX gateway edge intercepts and approves CORS preflight OPTIONS request."""
    gateway_url = (
        f"{apisix_settings.apisix_gateway_url.rstrip('/')}/api/v1/auth/sso-login"
    )

    async with httpx.AsyncClient() as client:
        try:
            res = await client.options(
                gateway_url,
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type,Authorization",
                },
                timeout=5.0,
            )
            assert res.status_code == 200
            assert (
                res.headers.get("Access-Control-Allow-Origin")
                == "http://localhost:3000"
            )
            assert res.headers.get("Access-Control-Allow-Credentials") == "true"
            assert "POST" in res.headers.get("Access-Control-Allow-Methods", "")
        except httpx.ConnectError:
            pytest.skip("APISIX gateway proxy not running on port 9080")
