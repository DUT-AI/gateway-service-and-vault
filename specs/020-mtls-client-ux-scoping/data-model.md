# Data Model: mTLS Client Ownership Scoping

**Feature**: `020-mtls-client-ux-scoping` | **Date**: 2026-11-25

No database schema changes are required. Existing entities used:

## 1. `RegisteredClientEntity` (`registered_clients`)
- `id: str` (ULID)
- `client_type: ClientType` (`USER_DEVICE` | `APP_SERVER`)
- `name: str`
- `owner_id: str` — Strictly populated as `str(user_ctx.user_id)` on creation.
- `cert_fingerprint: str` (SHA-256)
- `cert_serial: str`
- `expires_at: datetime`
- `is_revoked: bool`

## 2. `VirtualAccessKeyEntity` (`virtual_access_keys`)
- `id: str`
- `client_id: str` (FK -> `registered_clients.id`)
- `project_id: str` (FK -> `projects.id`)
- `key_prefix: str`
- `status: KeyStatus` (`ACTIVE` | `REVOKED` | `EXPIRED`)
