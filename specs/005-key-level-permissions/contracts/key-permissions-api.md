# API Contract: Granular Key-Level Permissions & Secret Access

**Base Route**: `/api/v1/vault/projects/{project_id}`  

---

## 1. Permission Management Endpoints

### A. Grant Key Permission to Identity
- **Method**: `POST`
- **Path**: `/api/v1/vault/projects/{project_id}/permissions`
- **Headers**:
  - `Content-Type`: `application/json`
  - `X-Actor-Id`: string (Administrator identity)
- **Request Body**:
  ```json
  {
    "identity_id": "client_payment_service",
    "identity_type": "client",
    "secret_key": "STRIPE_SECRET_KEY"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "id": "01JEABCDEF1234567890",
    "project_id": "01JE1234567890ABCDEF",
    "identity_id": "client_payment_service",
    "identity_type": "client",
    "secret_key": "STRIPE_SECRET_KEY",
    "granted_by": "admin",
    "created_at": "2026-11-23T03:30:00Z"
  }
  ```

---

### B. Revoke Key Permission from Identity
- **Method**: `DELETE`
- **Path**: `/api/v1/vault/projects/{project_id}/permissions`
- **Headers**:
  - `X-Actor-Id`: string (Administrator identity)
- **Query Parameters**:
  - `identity_id`: string (required)
  - `secret_key`: string (required)
- **Response**: `204 No Content`

---

### C. List Permitted Keys for Identity
- **Method**: `GET`
- **Path**: `/api/v1/vault/projects/{project_id}/permissions`
- **Query Parameters**:
  - `identity_id`: string (required)
- **Response**: `200 OK`
  ```json
  {
    "project_id": "01JE1234567890ABCDEF",
    "identity_id": "client_payment_service",
    "permitted_keys": [
      "DATABASE_URL",
      "STRIPE_SECRET_KEY"
    ]
  }
  ```

---

## 2. Granular Secret Retrieval Endpoint

### Request
- **Method**: `GET`
- **Path**: `/api/v1/vault/projects/{project_id}/secrets`
- **Headers**:
  - `X-Identity-Id`: string (required — caller's user ID or machine client ID)
  - `Authorization`: `Bearer <token>` (optional, fallback to extract identity from token)
- **Query Parameters**:
  - `scope`: string (optional, filter by secret scope)
  - `key`: string (optional, request a specific single key)

### Behavior & Enforcement Rules
1. The server loads all permitted keys for `X-Identity-Id` in `project_id`.
2. If `key` query parameter is provided:
   - If `key` is NOT in the caller's permitted keys (and caller does not have wildcard `*`), server returns `403 Forbidden`:
     ```json
     {
       "detail": "Access denied: Identity does not have permission to access secret key 'STRIPE_SECRET_KEY'"
     }
     ```
3. If no specific `key` is requested:
   - Server decrypts and returns **ONLY** keys matching the caller's permitted list.
   - Any secret key in the project not permitted to the caller is omitted completely.
   - If caller has zero permitted keys, response returns empty scopes `{}`.

### Success Response (`200 OK`)
```json
{
  "project_id": "01JE1234567890ABCDEF",
  "scopes": {
    "common": {
      "DATABASE_URL": "postgresql://user:pass@db:5432/app"
    },
    "payment": {
      "STRIPE_SECRET_KEY": "sk_live_12345"
    }
  }
}
```
*(Notice: Any other secrets in `common` or `payment` not granted to this identity are not included in the response).*

---

## 3. Key-Filtered Server-Sent Events (SSE) Stream

### Request
- **Method**: `GET`
- **Path**: `/api/v1/vault/projects/{project_id}/stream`
- **Headers**:
  - `Accept`: `text/event-stream`
  - `X-Identity-Id`: string (caller identity)

### Behavior
- When a secret is updated on the Control Plane:
  - If the modified key is in the caller's permitted keys (or caller has `*`):
    - Yields `event: secret_update\ndata: {"changed_keys": ["DATABASE_URL"], ...}\n\n`
  - If the modified key is NOT permitted to the caller:
    - Suppresses the notification completely (zero event transmitted).
