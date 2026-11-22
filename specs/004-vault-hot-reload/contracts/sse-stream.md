# API Contract: Vault Server-Sent Events (SSE) Stream

**Protocol**: HTTP/1.1 & HTTP/2 Server-Sent Events (`text/event-stream`)  
**Base Route**: `/api/v1/vault/projects/{project_id}/stream`  

---

## 1. Stream Connection Endpoint

### Request
- **Method**: `GET`
- **Path**: `/api/v1/vault/projects/{project_id}/stream`
- **Headers**:
  - `Accept`: `text/event-stream` (required)
  - `X-User-Role`: string (optional, defaults to `"user"`)
  - `X-Actor-Id`: string (optional, caller identity)
  - `Authorization`: `Bearer <token>` (optional, if using JWT)
- **Query Parameters**:
  - `scope`: string (optional) — filter notifications for a specific secret scope (e.g., `common`, `financial`, `production`).

### Response Headers
- `Content-Type`: `text/event-stream; charset=utf-8`
- `Cache-Control`: `no-cache, no-transform`
- `Connection`: `keep-alive`
- `X-Accel-Buffering`: `no` (instructs NGINX / reverse proxies not to buffer chunks)

---

## 2. Event Stream Payloads

All events conform to the standard SSE framing: `event: <name>\ndata: <json>\n\n`.

### A. Connection Acknowledged (`connected`)
Transmitted immediately when the client establishes the SSE connection.

```text
event: connected
data: {"project_id": "proj_demo", "status": "active", "timestamp": "2026-11-23T03:00:00Z"}

```

### B. Heartbeat Ping (`ping`)
Transmitted every 15 seconds of inactivity to keep connections alive through proxies and firewalls.

```text
event: ping
data: {"timestamp": "2026-11-23T03:00:15Z"}

```

### C. Secret Update Notification (`secret_update`)
Transmitted whenever a secret in the project is created, updated, or revoked.

```text
event: secret_update
data: {"event_id": "01JEABCDEF1234567890", "project_id": "proj_demo", "scope_name": "common", "changed_keys": ["DATABASE_URL", "CACHE_TTL"], "new_version": 4, "actor": "admin_user", "timestamp": "2026-11-23T03:01:23.456Z"}

```

**Payload Schema**:
| Field | Type | Description |
|---|---|---|
| `event_id` | `string` | Unique ULID identifying this event. |
| `project_id` | `string` | Target project ID. |
| `scope_name` | `string` | Scope where changes occurred (`common`, `financial`, etc.). |
| `changed_keys` | `string[]` | Array of modified/created configuration key names. |
| `new_version` | `integer` | Monotonically increasing version number. |
| `actor` | `string` | User or service identity who authored the change. |
| `timestamp` | `string` | UTC ISO-8601 timestamp. |

---

## 3. Error Responses

- **403 Forbidden**: Client does not have permission for the specified project or requested scope.
  ```json
  {
    "detail": "Permission denied for requested secret scope"
  }
  ```
- **404 Not Found**: Specified `project_id` does not exist.
  ```json
  {
    "detail": "Project not found"
  }
  ```
