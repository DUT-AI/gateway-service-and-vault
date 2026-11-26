# Research: Delete Vault Environment Variable

**Feature**: `023-delete-vault-secret`
**Date**: 2026-11-26

## Decisions & Rationale

### 1. HTTP Endpoint Design (`DELETE /api/v1/vault/projects/{project_id}/secrets`)
- **Decision**: Use query parameters `scope_name: str = Query(...)` and `key: str = Query(...)` on `DELETE /api/v1/vault/projects/{project_id}/secrets`.
- **Rationale**: Standard HTTP `DELETE` with query params avoids proxy/Axios body stripping issues, matches `DELETE /api/v1/vault/projects/{project_id}/permissions`, and cleanly targets the natural unique key `(project_id, scope_name, key)`.
- **Alternatives considered**: `DELETE /secrets/{secret_id}` — rejected because `SecretsTable` and `FlatSecretItem` operate by `(scope_name, key)` and `GetSecretsResponse` returns `{ scopes: { scope_name: { key: value } } }` without exposing row IDs.

### 2. Key Permission Cleanup on Deletion
- **Decision**: Delete the secret row in `SqlSecretRepository.delete_secret(project_id, scope_name, key)` (cascading `secret_versions` via ORM/FK `ondelete="CASCADE"`). Only clean up `key_permissions` for `(project_id, key)` if no other scope in the same project contains `key` (or keep `key_permissions` isolated from `SecretRepository` via `IKeyPermissionRepository` inside `DeleteSecretUseCase` to preserve Repository Isolation).
- **Rationale**: Preserves Constitution Principle I (zero cross-aggregate queries inside `SecretRepository`) and handles the edge case where `Common/API_KEY` and `Production/API_KEY` coexist.

### 3. Role-Based Authorization (`RoleTier.OTHER`)
- **Decision**: In `DeleteSecretUseCase.execute(..., require_permission_for_identity: str | None = None)`:
  - `ADMIN` and `PROJECT_DEVELOPER` (after `ensure_project_access`) pass `require_permission_for_identity=None` -> allowed to delete any key in the project.
  - `RoleTier.OTHER` passes `require_permission_for_identity=str(user_ctx.user_id)` -> `DeleteSecretUseCase` checks `await self.permission_repo.get_permitted_keys_for_identity(project_id, identity_id)`; if `key not in permitted_keys`, raises `ForbiddenError` (`403`).
- **Rationale**: Matches `CreateSecretUseCase` and `GetSecretsByScopeUseCase` where `RoleTier.OTHER` access is strictly scoped to granted `key_permissions`.

### 4. Real-Time SSE Propagation
- **Decision**: Publish `ConfigChangeEvent(project_id=project_id, scope_name=scope_name, changed_keys=[key], new_version=0, actor=actor)` via `IVaultBroadcaster` after deletion.
- **Rationale**: Reuses the existing `ConfigChangeEvent` / Redis Pub/Sub / SSE pipeline without breaking schema compatibility.
