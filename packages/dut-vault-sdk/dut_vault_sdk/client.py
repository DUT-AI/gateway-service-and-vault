import asyncio
import base64
import logging
import os
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from dut_vault_sdk.store import InMemoryConfigStore

logger = logging.getLogger("dut_vault_sdk")


def _load_client_signer(
    cert_pair: tuple[str, str] | None,
) -> tuple[str, str, rsa.RSAPrivateKey] | None:
    """Load SHA-256 fingerprint, base64 PEM cert, and RSA private key from (client.crt, client.key)."""
    if not cert_pair:
        return None
    crt_path, key_path = cert_pair
    try:
        crt_bytes = Path(crt_path).read_bytes()
        cert = x509.load_pem_x509_certificate(crt_bytes)
        fingerprint = cert.fingerprint(hashes.SHA256()).hex()
        cert_b64 = base64.b64encode(crt_bytes).decode("ascii")
        private_key = serialization.load_pem_private_key(
            Path(key_path).read_bytes(), password=None
        )
        if not isinstance(private_key, rsa.RSAPrivateKey):
            return None
        return fingerprint, cert_b64, private_key
    except Exception:
        return None


def resolve_mtls_cert(
    cert_path: str | None = None, key_path: str | None = None
) -> tuple[str, str] | None:
    """Resolve (client.crt, client.key) from explicit args, env vars, or ~/.dut-vault/."""
    crt = cert_path or os.environ.get("SSL_CERT_FILE")
    key = key_path or os.environ.get("SSL_KEY_FILE")
    if crt and key:
        return (crt, key)

    default_dir = Path.home() / ".dut-vault"
    default_crt = default_dir / "client.crt"
    default_key = default_dir / "client.key"
    if default_crt.is_file() and default_key.is_file():
        return (str(default_crt), str(default_key))
    return None


class VaultClient:
    """In-memory client for dynamic configuration fetching and real-time hot-reloading."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        project_id: str = "default",
        user_role: str = "user",
        identity_id: str | None = None,
        scope: str | None = None,
        inject_environ: bool = True,
        auto_reconnect: bool = True,
        max_events: int | None = None,
        virtual_key: str | None = None,
        cert_path: str | None = None,
        key_path: str | None = None,
        http_client: httpx.Client | httpx.AsyncClient | None = None,
        stream_http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.project_id = project_id
        self.user_role = user_role
        self.identity_id = identity_id
        self.scope = scope
        self.auto_reconnect = auto_reconnect
        self.max_events = max_events
        self.virtual_key = virtual_key or os.environ.get("X_VIRTUAL_KEY")
        self._cert = resolve_mtls_cert(cert_path, key_path)
        self._signer = _load_client_signer(self._cert)
        self.store = InMemoryConfigStore(inject_environ=inject_environ)

        default_headers: dict[str, str] = {}
        if self.virtual_key:
            default_headers["X-Virtual-Key"] = self.virtual_key

        self._custom_http = http_client
        if isinstance(http_client, httpx.AsyncClient):
            self._async_http = http_client
            self._sync_http = None
        elif isinstance(http_client, httpx.Client):
            self._sync_http = http_client
            self._async_http = None
        else:
            client_kwargs: dict[str, Any] = {
                "timeout": 10.0,
                "headers": default_headers,
                "event_hooks": {"request": [self._sign_request_sync]},
            }
            if self._cert is not None:
                client_kwargs["cert"] = self._cert
            self._sync_http = httpx.Client(**client_kwargs)
            async_kwargs: dict[str, Any] = {
                "timeout": 10.0,
                "headers": default_headers,
                "event_hooks": {"request": [self._sign_request_async]},
            }
            if self._cert is not None:
                async_kwargs["cert"] = self._cert
            self._async_http = httpx.AsyncClient(**async_kwargs)

        if stream_http_client is not None:
            self._stream_http = stream_http_client
        else:
            stream_kwargs: dict[str, Any] = {
                "timeout": 60.0,
                "headers": default_headers,
                "event_hooks": {"request": [self._sign_request_async]},
            }
            if self._cert is not None:
                stream_kwargs["cert"] = self._cert
            self._stream_http = httpx.AsyncClient(**stream_kwargs)

        self._stop_event = threading.Event()
        self._connected_event = threading.Event()
        self._stream_thread: threading.Thread | None = None
        self._stream_task: asyncio.Task[Any] | None = None

    def fetch_secrets(self) -> dict[str, str]:
        """Synchronously fetch latest authorized decrypted secrets into process RAM."""
        url = f"{self.base_url}/api/v1/vault/projects/{self.project_id}/secrets"
        params: dict[str, str] = {}
        if self.scope:
            params["scope"] = self.scope

        headers = {
            "x-identity-id": self.identity_id or self.user_role,
            "x-user-role": self.user_role,
        }

        if self._sync_http is not None:
            response = self._sync_http.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        else:
            # Fallback if only async client is provided
            data = asyncio.run(self.fetch_secrets_async())
            return data

        scopes = data.get("scopes", {})
        all_secrets: dict[str, str] = {}
        for kv_pairs in scopes.values():
            all_secrets.update(kv_pairs)

        self.store.update_bulk(all_secrets)
        return all_secrets

    async def fetch_secrets_async(self) -> dict[str, str]:
        """Asynchronously fetch latest authorized decrypted secrets into process RAM."""
        url = f"{self.base_url}/api/v1/vault/projects/{self.project_id}/secrets"
        params: dict[str, str] = {}
        if self.scope:
            params["scope"] = self.scope

        headers = {
            "x-identity-id": self.identity_id or self.user_role,
            "x-user-role": self.user_role,
        }
        client = self._async_http or httpx.AsyncClient(timeout=10.0)
        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        finally:
            if client is not self._async_http:
                await client.aclose()

        scopes = data.get("scopes", {})
        all_secrets: dict[str, str] = {}
        for kv_pairs in scopes.values():
            all_secrets.update(kv_pairs)

        self.store.update_bulk(all_secrets)
        return all_secrets

    async def _async_stream_worker(self) -> None:
        """Asynchronous worker listening to SSE event stream."""
        stream_url = f"{self.base_url}/api/v1/vault/projects/{self.project_id}/stream"
        params: dict[str, str] = {}
        if self.scope:
            params["scope"] = self.scope
        if self.max_events is not None:
            params["max_events"] = str(self.max_events)

        headers = {
            "Accept": "text/event-stream",
            "x-identity-id": self.identity_id or self.user_role,
            "x-user-role": self.user_role,
        }

        client = self._stream_http

        while not self._stop_event.is_set():
            try:
                async with client.stream(
                    "GET", stream_url, params=params, headers=headers, timeout=60.0
                ) as resp:
                    resp.raise_for_status()
                    current_event_type = "message"

                    async for line in resp.aiter_lines():
                        if self._stop_event.is_set():
                            break
                        if not line:
                            continue

                        if line.startswith("event:"):
                            current_event_type = line[len("event:") :].strip()
                        elif line.startswith("data:"):
                            if current_event_type == "connected":
                                self._connected_event.set()
                            elif current_event_type == "secret_update":
                                try:
                                    await self.fetch_secrets_async()
                                except Exception as err:
                                    logger.warning(
                                        "Failed to refresh secrets after SSE event: %s",
                                        err,
                                    )
                            current_event_type = "message"
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self._stop_event.is_set():
                    break
                logger.debug("SSE stream connection lost: %s. Retrying...", e)
                await asyncio.sleep(1.0 if self.auto_reconnect else 0.1)
                if not self.auto_reconnect:
                    break

    def _sync_stream_worker(self) -> None:
        """Thread worker running async stream worker inside an independent event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._async_stream_worker())
        finally:
            loop.close()

    def connect(self, wait_for_stream: bool = False, timeout: float = 3.0) -> None:
        """Synchronously fetch initial secrets into RAM and start background stream thread."""
        self.fetch_secrets()
        self._stop_event.clear()
        self._connected_event.clear()
        self._stream_thread = threading.Thread(
            target=self._sync_stream_worker,
            name=f"vault-stream-{self.project_id}",
            daemon=True,
        )
        self._stream_thread.start()
        if wait_for_stream:
            self._connected_event.wait(timeout=timeout)

    async def connect_async(
        self, wait_for_stream: bool = False, timeout: float = 3.0
    ) -> None:
        """Asynchronously fetch initial secrets into RAM and start streaming task."""
        await self.fetch_secrets_async()
        self._stop_event.clear()
        self._connected_event.clear()
        self._stream_task = asyncio.create_task(self._async_stream_worker())
        if wait_for_stream:
            start = time.time()
            while not self._connected_event.is_set() and time.time() - start < timeout:
                await asyncio.sleep(0.05)

    def disconnect(self) -> None:
        """Stop background streaming thread."""
        self._stop_event.set()
        if self._stream_thread and self._stream_thread.is_alive():
            self._stream_thread.join(timeout=2.0)

    async def disconnect_async(self) -> None:
        """Stop background streaming task."""
        self._stop_event.set()
        if self._stream_task and not self._stream_task.done():
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass

    def get(self, key: str, default: str | None = None) -> str | None:
        return self.store.get(key, default)

    def get_all(self) -> dict[str, str]:
        return self.store.get_all()

    def on_change(
        self, key: str, callback: Callable[[str, str | None, str], Any]
    ) -> None:
        self.store.on_change(key, callback)

    def _sign_request_sync(self, request: httpx.Request) -> None:
        """Attach Proof-of-Possession signature headers signed by client.key."""
        if not self._signer:
            return
        fingerprint, cert_b64, private_key = self._signer
        ts = str(int(time.time()))
        payload = f"{ts}:{request.method.upper()}:{request.url.path}".encode()
        signature = private_key.sign(payload, padding.PKCS1v15(), hashes.SHA256())
        request.headers["X-Client-Fingerprint"] = fingerprint
        request.headers["X-Client-Cert"] = cert_b64
        request.headers["X-Client-Timestamp"] = ts
        request.headers["X-Client-Signature"] = base64.b64encode(signature).decode(
            "ascii"
        )

    async def _sign_request_async(self, request: httpx.Request) -> None:
        self._sign_request_sync(request)

    def _build_gateway_kwargs(
        self,
        service_slug: str | None = None,
        timeout: float = 30.0,
        is_async: bool = False,
    ) -> dict[str, Any]:
        headers: dict[str, str] = {}
        if self.virtual_key:
            headers["X-Virtual-Key"] = self.virtual_key
        if self.project_id and self.project_id != "default":
            headers["X-Project-Id"] = self.project_id
        hook = self._sign_request_async if is_async else self._sign_request_sync
        kwargs: dict[str, Any] = {
            "timeout": timeout,
            "headers": headers,
            "event_hooks": {"request": [hook]},
        }
        if service_slug:
            kwargs["base_url"] = f"{self.base_url}/services/{service_slug}"
        if self._cert is not None:
            kwargs["cert"] = self._cert
        return kwargs

    def gateway_client(
        self, service_slug: str | None = None, timeout: float = 30.0
    ) -> httpx.Client:
        """Create a pre-configured sync httpx.Client with mTLS cert, PoP signing, and X-Virtual-Key."""
        return httpx.Client(
            **self._build_gateway_kwargs(service_slug, timeout, is_async=False)
        )

    def async_gateway_client(
        self, service_slug: str | None = None, timeout: float = 30.0
    ) -> httpx.AsyncClient:
        """Create a pre-configured async httpx.AsyncClient with mTLS cert, PoP signing, and X-Virtual-Key."""
        return httpx.AsyncClient(
            **self._build_gateway_kwargs(service_slug, timeout, is_async=True)
        )
