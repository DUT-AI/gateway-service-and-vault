"""HTTP client for synchronizing routes, SSL, and consumers with Apache APISIX Admin API."""

from urllib.parse import urlparse

import httpx

from core.config import apisix_settings
from core.exceptions.base import DomainException


class ApisixSyncError(DomainException):
    def __init__(self, message: str = "Failed to sync with APISIX Admin API") -> None:
        super().__init__(message=message)


class ApisixAdminClient:
    """Manages APISIX dynamic routing, SSL, and consumers via Admin REST API."""

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

    async def sync_control_plane_route(
        self,
        backend_host: str | None = None,
        backend_port: int | None = None,
    ) -> dict:
        """Configure route so any request to /api/* through APISIX forwards to FastAPI Control Plane."""
        host = backend_host or apisix_settings.apisix_backend_host
        port = backend_port or apisix_settings.apisix_backend_port

        payload = {
            "name": "control_plane_backend_route",
            "uri": "/api/*",
            "upstream": {
                "type": "roundrobin",
                "scheme": "http",
                "nodes": {f"{host}:{port}": 1},
                "pass_host": "pass",
            },
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.put(
                    f"{self.admin_url}/apisix/admin/routes/control_plane_api",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as err:
                raise ApisixSyncError(
                    f"Error syncing control plane route to APISIX: {err}"
                ) from err

    async def sync_upstream_service_route(
        self,
        service_slug: str,
        upstream_base_url: str,
        upstream_auth_type: str,
        upstream_credential: str = "",
        rate_limit_rpm: int = 60,
    ) -> dict:
        """Create or update a dynamic route with upstream credential injection in APISIX."""
        route_id = f"route_{service_slug}"
        parsed = urlparse(upstream_base_url)
        scheme = parsed.scheme or "http"
        default_port = 443 if scheme == "https" else 80
        port = parsed.port or default_port
        host_node = f"{parsed.hostname}:{port}"
        base_path = parsed.path.rstrip("/")

        rewrite_headers = {}
        if upstream_auth_type.upper() == "BEARER_TOKEN" and upstream_credential:
            rewrite_headers["Authorization"] = f"Bearer {upstream_credential}"
        elif upstream_auth_type.upper() == "API_KEY" and upstream_credential:
            rewrite_headers["X-API-KEY"] = upstream_credential

        control_plane_url = f"http://{apisix_settings.apisix_backend_host}:{apisix_settings.apisix_backend_port}/api/v1/gateway/verify-binding"
        plugins: dict = {
            "proxy-rewrite": {
                "regex_uri": (
                    [f"^/services/{service_slug}/(.*)", f"{base_path}/$1"]
                    if base_path
                    else [f"^/services/{service_slug}/(.*)", "/$1"]
                ),
            },
            "identity-binding-filter": {
                "control_plane_url": control_plane_url,
            },
        }
        if rewrite_headers:
            plugins["proxy-rewrite"]["headers"] = rewrite_headers

        payload = {
            "name": f"route_{service_slug}",
            "uri": f"/services/{service_slug}/*",
            "plugins": plugins,
            "upstream": {
                "type": "roundrobin",
                "scheme": scheme,
                "nodes": {host_node: 1},
                "pass_host": "node" if scheme == "https" else "pass",
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
                raise ApisixSyncError(
                    f"Error syncing route '{route_id}' to APISIX: {err}"
                ) from err

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

    async def sync_ssl_certificate(
        self,
        ssl_id: str,
        cert_pem: str,
        key_pem: str,
        snis: list[str] | None = None,
        ca_pem: str | None = None,
    ) -> dict:
        """Register or update an SSL certificate object in APISIX for HTTPS/mTLS."""
        payload: dict = {
            "cert": cert_pem,
            "key": key_pem,
            "snis": snis or ["localhost", "127.0.0.1"],
        }
        if ca_pem:
            payload["client"] = {"ca": ca_pem, "depth": 2}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.put(
                    f"{self.admin_url}/apisix/admin/ssls/{ssl_id}",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as err:
                raise ApisixSyncError(
                    f"Error registering SSL certificate in APISIX: {err}"
                ) from err
