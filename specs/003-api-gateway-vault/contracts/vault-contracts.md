# Dynamic Vault REST API & Event Stream Contracts

This document formalizes the API endpoints for configuration secret management and real-time live synchronization under `modules/vault`.

---

## 1. REST Endpoints (`/api/v1/vault`)

### 1.1. Fetch Secrets by Project & Scope
- **Method**: `GET /api/v1/vault/projects/{project_id}/secrets`
- **Headers**: `Authorization: Bearer <user_jwt_from_sso>`
- **Query Params**: `scope: Optional[str] = None`
- **Response**: `HTTP 200 OK`
```json
{
  "project_id": "proj_01JABC1234567890",
  "scopes": {
    "Common": {
      "DATABASE_URL": "postgresql+asyncpg://app:secret@db:5432/app",
      "REDIS_URL": "redis://redis:6379/0",
      "APP_ENV": "development"
    },
    "Financial": {
      "PAYMENT_API_SECRET": "sec_live_99887766",
      "STRIPE_WEBHOOK_KEY": "whsec_abcdef123456"
    }
  },
  "version": 7,
  "fetched_at": "2026-11-23T02:40:00Z"
}
```
*Note: If the user lacks the Financial role, the `Financial` object is omitted.*

### 1.2. Upsert Secret Item
- **Method**: `POST /api/v1/vault/projects/{project_id}/secrets`
- **Headers**: `Authorization: Bearer <admin_or_lead_jwt>`
- **Request Body**:
```json
{
  "scope_name": "Financial",
  "key": "PAYMENT_API_SECRET",
  "value": "sec_live_new_value_12345"
}
```
- **Response**: `HTTP 201 Created`
```json
{
  "id": "sec_01JXYZ987654321",
  "project_id": "proj_01JABC1234567890",
  "scope_name": "Financial",
  "key": "PAYMENT_API_SECRET",
  "version": 8,
  "updated_at": "2026-11-23T02:40:05Z"
}
```

---

## 2. Server-Sent Events (SSE) Live Stream Contract

Application runtimes connect to this endpoint via SDK to receive real-time updates:

- **Method**: `GET /api/v1/vault/projects/{project_id}/stream`
- **Headers**: 
  - `Accept: text/event-stream`
  - `Authorization: Bearer <sso_token_or_client_token>`
- **Response**: `HTTP 200 OK` (Continuous stream)

### Event Messages:

#### Event 1: Initial Handshake
```text
event: connected
data: {"project_id": "proj_01JABC1234567890", "server_time": "2026-11-23T02:40:00Z", "current_version": 7}

```

#### Event 2: Secret Changed Notification
```text
event: secret_update
data: {"project_id": "proj_01JABC1234567890", "scope": "Financial", "changed_keys": ["PAYMENT_API_SECRET"], "new_version": 8, "timestamp": "2026-11-23T02:40:05Z"}

```

#### Event 3: Heartbeat (Keep-Alive every 15s)
```text
event: ping
data: {"time": "2026-11-23T02:40:20Z"}

```
