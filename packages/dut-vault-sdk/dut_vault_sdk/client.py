import asyncio
import logging
import threading
import time
from collections.abc import Callable
from typing import Any

import httpx

from dut_vault_sdk.store import InMemoryConfigStore

logger = logging.getLogger("dut_vault_sdk")


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
        self.store = InMemoryConfigStore(inject_environ=inject_environ)

        self._custom_http = http_client
        if isinstance(http_client, httpx.AsyncClient):
            self._async_http = http_client
            self._sync_http = None
        elif isinstance(http_client, httpx.Client):
            self._sync_http = http_client
            self._async_http = None
        else:
            self._sync_http = httpx.Client(timeout=10.0)
            self._async_http = httpx.AsyncClient(timeout=10.0)

        self._stream_http = stream_http_client or httpx.AsyncClient(timeout=60.0)

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
