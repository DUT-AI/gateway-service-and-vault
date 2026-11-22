import logging
import os
import threading
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("dut_vault_sdk.store")


class InMemoryConfigStore:
    """Thread-safe in-memory configuration store residing strictly in RAM."""

    def __init__(self, inject_environ: bool = True) -> None:
        self._data: dict[str, str] = {}
        self._lock = threading.RLock()
        self._version: int = 0
        self._inject_environ = inject_environ
        self._listeners: dict[str, list[Callable[[str, str | None, str], Any]]] = {}

    @property
    def version(self) -> int:
        with self._lock:
            return self._version

    def get(self, key: str, default: str | None = None) -> str | None:
        """Thread-safe retrieval of configuration key from RAM."""
        with self._lock:
            return self._data.get(key, default)

    def get_all(self) -> dict[str, str]:
        """Return a thread-safe snapshot copy of all configuration keys in RAM."""
        with self._lock:
            return dict(self._data)

    def on_change(
        self, key: str, callback: Callable[[str, str | None, str], Any]
    ) -> None:
        """Register a callback hook invoked when a key is modified."""
        with self._lock:
            if key not in self._listeners:
                self._listeners[key] = []
            self._listeners[key].append(callback)

    def update_bulk(
        self, updates: dict[str, str], version: int | None = None
    ) -> list[str]:
        """
        Atomically update multiple keys in memory and optionally synchronize os.environ.
        Executes registered on_change callbacks for all changed values.
        """
        changed_keys: list[str] = []
        callbacks_to_invoke: list[
            tuple[Callable[[str, str | None, str], Any], str, str | None, str]
        ] = []

        with self._lock:
            for k, new_v in updates.items():
                old_v = self._data.get(k)
                if old_v != new_v:
                    self._data[k] = new_v
                    if self._inject_environ:
                        os.environ[k] = new_v
                    changed_keys.append(k)

                    # Gather specific key callbacks
                    for cb in self._listeners.get(k, []):
                        callbacks_to_invoke.append((cb, k, old_v, new_v))
                    # Gather wildcard callbacks
                    for cb in self._listeners.get("*", []):
                        callbacks_to_invoke.append((cb, k, old_v, new_v))

            if version is not None:
                self._version = version

        # Invoke callbacks
        for cb, k, old_v, new_v in callbacks_to_invoke:
            try:
                cb(k, old_v, new_v)
            except Exception as err:
                logger.warning("Callback error for key %s: %s", k, err)

        return changed_keys

    def clear(self) -> None:
        """Clear in-memory store."""
        with self._lock:
            if self._inject_environ:
                for k in self._data:
                    os.environ.pop(k, None)
            self._data.clear()
            self._version = 0
