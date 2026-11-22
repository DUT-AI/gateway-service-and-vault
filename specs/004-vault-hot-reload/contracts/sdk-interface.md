# Client Contract: `dut-vault-sdk` Interface

**Target Package**: `packages/dut-vault-sdk/`  
**Compatibility**: Python 3.10+  
**Operating Principle**: 100% In-Memory RAM Storage. Zero plaintext `.env` files written to disk.

---

## 1. Programmatic Python SDK Interface

### Class `VaultClient`

```python
from collections.abc import Callable
from typing import Any

class VaultClient:
    """In-memory client for dynamic configuration fetching and real-time hot-reloading."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        project_id: str = "default",
        user_role: str = "user",
        scope: str | None = None,
        inject_environ: bool = True,
        auto_reconnect: bool = True,
    ) -> None: ...

    def connect(self) -> None:
        """
        Synchronously fetches initial secrets into RAM and starts the background
        SSE listener daemon thread.
        """
        ...

    async def connect_async(self) -> None:
        """Asynchronous variant of connect for asyncio applications."""
        ...

    def disconnect(self) -> None:
        """Stops the background SSE streaming listener cleanly."""
        ...

    def get(self, key: str, default: str | None = None) -> str | None:
        """Thread-safe retrieval of a configuration variable from process RAM."""
        ...

    def get_all(self) -> dict[str, str]:
        """Returns a snapshot copy of all decrypted configuration variables currently in RAM."""
        ...

    def on_change(
        self,
        key: str,
        callback: Callable[[str, str | None, str], Any],
    ) -> None:
        """
        Registers a callback hook invoked when a specific key changes.
        Signature: callback(key: str, old_val: str | None, new_val: str)
        """
        ...
```

---

## 2. CLI Process Runner Interface

The CLI runner injects configuration directly into the process environment in RAM, launching any child application without creating disk files.

### Command Usage
```bash
python -m dut_vault_sdk run --project <PROJECT_ID> [options] -- <COMMAND> [ARGS...]
```

### Options
- `--api-url <url>`: Centralized Control Plane URL (defaults to `http://localhost:8000` or `$DUT_VAULT_URL`).
- `--project <id>`: Project ID (defaults to `$DUT_VAULT_PROJECT`).
- `--scope <scope>`: Secret scope to load (defaults to all authorized scopes).
- `--role <role>`: Client role header (defaults to `user`).
- `--no-watch`: Load secrets into RAM once on startup without maintaining a background hot-reload stream.

### Example
```bash
python -m dut_vault_sdk run --project proj_alpha --scope production -- uvicorn myapp:app --port 8080
```
- Process launches immediately with secrets accessible in `os.environ`.
- Zero `.env` files are created or read.
- When an update event occurs on the Control Plane, `os.environ` is updated in-place and a signal/log is emitted.
