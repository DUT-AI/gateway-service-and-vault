# Phase 1: Data Model - Real-Time Dynamic Vault Hot-Reload

**Feature**: `004-vault-hot-reload`  
**Date**: 2026-11-23  
**Status**: Completed  

---

## 1. Domain Entities (`modules/vault/domain/entities.py`)

Pure Python dataclasses with zero framework dependencies.

### `ConfigChangeEvent`
Represents the domain event emitted when one or more secrets are modified, created, or revoked within a project and scope.

```python
@dataclass
class ConfigChangeEvent:
    project_id: str
    scope_name: str
    changed_keys: list[str]
    new_version: int
    actor: str = ""
    event_id: str = field(default_factory=generate_ulid)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "project_id": self.project_id,
            "scope_name": self.scope_name,
            "changed_keys": self.changed_keys,
            "new_version": self.new_version,
            "actor": self.actor,
            "timestamp": self.timestamp.isoformat(),
        }
```

**Validation & Invariants**:
- `project_id`: Non-empty string.
- `scope_name`: Non-empty string, normalized to lowercase for comparisons.
- `changed_keys`: List containing at least 1 secret key name.
- `new_version`: Strictly positive integer (`>= 1`), monotonically increasing for the mutated secret.

---

## 2. Application & API DTOs (`modules/vault/dtos/vault_dtos.py`)

Pydantic v2 schemas used for HTTP serialization, SSE event payloads, and API requests.

### `SecretUpdateEventPayload`
Serialized JSON body transmitted in the `data:` field of an SSE `secret_update` event.

```python
class SecretUpdateEventPayload(BaseModel):
    event_id: str
    project_id: str
    scope_name: str
    changed_keys: list[str]
    new_version: int
    actor: str = ""
    timestamp: str  # ISO-8601 UTC string
```

### `StreamPingPayload`
Periodic heartbeat message sent every 15 seconds to keep proxies from dropping idle SSE connections.

```python
class StreamPingPayload(BaseModel):
    timestamp: str  # ISO-8601 UTC string
```

---

## 3. Client-Side Runtime Data Models (`packages/dut-vault-sdk/`)

Pure in-memory models running in client process RAM.

### `InMemoryConfigStore`
Thread-safe runtime key-value store holding the client application's decrypted configuration.

- **Attributes**:
  - `_data: dict[str, str]`: Internal dictionary mapping `KEY -> VALUE`.
  - `_lock: threading.RLock`: Reentrant lock ensuring atomic reads, bulk replacements, and single-key updates across multi-threaded applications.
  - `_version: int`: Local version marker of current config state.
  - `_listeners: dict[str, list[Callable[[str, str, str], None]]]`: Callbacks registered for key mutations `(key, old_value, new_value)`.
- **Methods**:
  - `get(key: str, default: str | None = None) -> str | None`: Thread-safe retrieval.
  - `get_all() -> dict[str, str]`: Thread-safe copy of all active configuration keys.
  - `update_bulk(updates: dict[str, str], version: int) -> list[str]`: Atomically updates multiple keys, updates `os.environ` (if enabled), updates `_version`, and triggers callbacks for modified keys. Returns list of modified keys.
  - `on_change(key: str, callback: Callable[[str, str, str], None]) -> None`: Registers a change hook.

### `StreamSubscriptionState`
State machine tracking the SDK background connection.

```text
[DISCONNECTED] ──(connect)──> [CONNECTING] ──(SSE 200 OK)──> [CONNECTED / STREAMING]
      ▲                              │                                │
      │                              ▼ (network drop / timeout)        │
      └────────────────────── [RECONNECTING (Backoff)] ◄──────────────┘
```

- **States**:
  - `DISCONNECTED`: Initial state or explicitly stopped.
  - `CONNECTING`: Establishing HTTP GET request to `/api/v1/vault/projects/{id}/stream`.
  - `CONNECTED`: Active SSE stream receiving events or heartbeat pings.
  - `RECONNECTING`: Connection lost; sleeping for jittered backoff interval before next connection attempt.
