# API Contract: Server-Sent Events (SSE) Vault Stream

**Feature**: `009-web-vault-sse-sync`  
**Date**: 2026-11-23  

## 1. Endpoint Specification

Real-time unidirectional stream delivering configuration changes to authorized web clients and SDKs.

- **URL**: `/api/v1/vault/projects/{project_id}/stream`
- **Method**: `GET`
- **Path Parameters**:
  - `project_id` (string, required): ULID or unique identifier of the project workspace.
- **Query Parameters**:
  - `identity_id` (string, optional): Identity identifier of the user (e.g. `"1"` or `"admin"`) for key-level ACL filtering.
  - `scope` (string, optional): Specific scope name to listen to (e.g. `Database`).
  - `max_events` (integer, optional): Maximum events to yield before closing stream (used in automated tests).
- **Request Headers**:
  - `Cookie`: `access_token=<sso_token>` (automatic via browser withCredentials)
  - `Authorization`: `Bearer <token>` (if connecting via custom fetch stream)
  - `X-Identity-Id`: (Optional) Alternate caller identity header.
- **Response Headers**:
  - `Content-Type`: `text/event-stream`
  - `Cache-Control`: `no-cache, no-transform`
  - `Connection`: `keep-alive`
  - `X-Accel-Buffering`: `no`

---

## 2. Event Payloads

### A. Connection Established (`event: connected`)
Sent immediately when a client subscribes to the project's Redis Pub/Sub channel.

```text
event: connected
data: {"project_id": "01JD27M508E9D0V2V1Z9Q1ABC0", "status": "active", "timestamp": "2026-11-23T06:45:00.123456Z"}
```

### B. Configuration Secret Updated (`event: secret_update`)
Dispatched whenever an authorized secret is created or modified in the project.

```text
event: secret_update
data: {"event_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "project_id": "01JD27M508E9D0V2V1Z9Q1ABC0", "scope_name": "Database", "changed_keys": ["DB_PASSWORD"], "new_version": 2, "actor": "huynhphuocnguyen.dev@gmail.com", "timestamp": "2026-11-23T06:45:10.000000Z"}
```

### C. Heartbeat Ping (`event: ping`)
Dispatched every 15 seconds of inactivity to verify connection liveness.

```text
event: ping
data: {"timestamp": "2026-11-23T06:45:25.000000Z"}
```

---

## 3. Key-Level Permission Filtering Invariant

When `event: secret_update` is ready to broadcast:
1. The stream handler checks the caller's permitted keys (`ISecretRepository.get_permitted_keys_for_identity`).
2. If the caller is an `admin` or has `*` permission, the event is transmitted.
3. If the caller has granular permissions, the event is ONLY transmitted if at least one key in `changed_keys` is in the caller's permitted keys set.
4. If the caller does not have permission for any changed keys, the event is dropped silently for that caller.
