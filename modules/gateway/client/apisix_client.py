"""HTTP client for synchronizing routes and consumers with Apache APISIX Admin API."""

import httpx

from core.config import apisix_settings
from core.exceptions.base import DomainException


class ApisixSyncError(DomainException):
    def __init__(self, message: str = "Failed to sync with APISIX Admin API") -> None:
        super().__init__(message=message)


class ApisixAdminClient:
    """Manages APISIX dynamic routing and consumers via Admin REST API."""

    def __init__(
        self,
        admin_url: str | None = None,
        admin_key: str | None = None,
    ) -> None:
        self.admin_url = (admin_url or apisix_settings.apisix_admin_url).rstrip("/")
        self.admin_key = admin_key or apisix_settings.apisix_admin_key
        self.headers = {
            "X-API-KEY": self.admin_key,
            "Content-Type": "application/json",
        }

    async def put_route(
        self,
        route_id: str,
        service_slug: str,
        upstream_base_url: str,
        upstream_auth_type: str,
        upstream_credential: str,
        rate_limit_rpm: int = 60,
    ) -> dict:
        """Create or update a dynamic route with upstream credential injection in APISIX."""
        # Clean host and port from upstream_base_url
        url_stripped = upstream_base_url.replace("https://", "").replace("http://", "")
        nodes = {url_stripped: 1}

        # Build proxy rewrite headers
        rewrite_headers = {}
        if upstream_auth_type.upper() == "BEARER_TOKEN":
            rewrite_headers["Authorization"] = f"Bearer {upstream_credential}"
        elif upstream_auth_type.upper() == "API_KEY":
            rewrite_headers["X-API-KEY"] = upstream_credential

        payload = {
            "name": f"route_{service_slug}",
            "uri": f"/services/{service_slug}/*",
            "plugins": {
                "proxy-rewrite": {
                    "regex_uri": [f"^/services/{service_slug}/(.*)", "/$1"],
                    "headers": rewrite_headers,
                },
                "identity-binding-filter": {},
                "limit-count": {
                    "count": rate_limit_rpm,
                    "time_window": 60,
                    "rejected_code": 429,
                    "key": "header_X-Virtual-Key",
                    "policy": "redis",
                    "redis_host": "redis",
                    "redis_port": 6379,
                },
            },
            "upstream": {
                "type": "roundrobin",
                "nodes": nodes,
            },
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.put(
                    f"{self.admin_url}/apisix/admin/routes/{route_id}",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as err:
                raise ApisixSyncError(f"Error calling APISIX Admin API: {err}") from err

    async def delete_route(self, route_id: str) -> bool:
        """Remove a route from APISIX."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.delete(
                    f"{self.admin_url}/apisix/admin/routes/{route_id}",
                    headers=self.headers,
                )
                return response.status_code in [200, 204]
            except httpx.HTTPError as err:
                raise ApisixSyncError(
                    f"Error deleting route from APISIX: {err}"
                ) from err
