# API Contracts: mTLS Client & Key Ownership Scoping

**Feature**: `020-mtls-client-ux-scoping` | **Date**: 2026-11-25

## 1. `GET /api/v1/gateway/clients`
- **Auth**: `ADMIN` or `PROJECT_DEVELOPER` (`403` for `OTHER`).
- **Behavior**:
  - `ADMIN`: Returns all `RegisteredClientEntity` records across all owners.
  - `PROJECT_DEVELOPER`: Returns only records where `owner_id == str(user_ctx.user_id)`.

## 2. `POST /api/v1/gateway/clients`
- **Auth**: `ADMIN` or `PROJECT_DEVELOPER`.
- **Request Body**:
  ```json
  {
    "name": "MacBook Pro M3",
    "client_type": "USER_DEVICE",
    "validity_days": 30
  }
  ```
  *(Optional `owner_id` field, if sent, is ignored and overridden by `str(user_ctx.user_id)`).*
- **Response `201 Created`**: `RegisterClientResponse` with `owner_id == str(user_ctx.user_id)`.

## 3. `POST /api/v1/gateway/clients/{client_id}/revoke`
- **Auth**: `ADMIN` or `PROJECT_DEVELOPER`.
- **Behavior**:
  - `ADMIN`: Can revoke any existing client (`200 OK`).
  - `PROJECT_DEVELOPER`: Can revoke only if `client.owner_id == str(user_ctx.user_id)`. Otherwise returns `403 Forbidden`.
