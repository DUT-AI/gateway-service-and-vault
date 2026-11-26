# Feature Specification: Delete Vault Environment Variable

**Feature Branch**: `023-delete-vault-secret`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "Tôi muốn thêm chức năng xóa key env nữa"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete an Environment Variable from Project Vault (Priority: P1)

An authorized project member opens the **Biến môi trường (Vault)** tab of a project, clicks the **Xóa** (Delete) action on a secret row, confirms the irreversible deletion in a confirmation dialog, and sees the variable immediately removed from the Vault table and scope counts.

**Why this priority**: Currently users can create and edit environment variables in Vault, but have no way to remove obsolete, mistyped, or rotated keys from either the UI or API.

**Independent Test**: Create a secret `TEMP_KEY` in a project's `Common` scope, delete it via `DELETE /api/v1/vault/projects/{project_id}/secrets` (and via the UI confirmation dialog), and verify `GET /secrets` no longer returns `TEMP_KEY`.

**Acceptance Scenarios**:

1. **Given** an authorized user viewing the Secrets table, **When** they click the Delete button on a row (`scope_name`, `key`), **Then** a confirmation dialog displays the key name and scope before performing deletion.
2. **Given** the user confirms deletion, **When** the delete request succeeds, **Then** the secret (and its version history) is deleted from the database, associated key-level permissions for that key are cleaned up if no other scope in the project holds the same key, and the UI refreshes immediately.
3. **Given** a request to delete a non-existent `(project_id, scope_name, key)`, **When** the API processes the request, **Then** it returns `HTTP 404 Not Found`.

---

### User Story 2 - 3-Tier RBAC & Key-Level Permission Enforcement (Priority: P2)

Deletion strictly enforces the platform's 3-tier RBAC and Project Membership rules so unauthorized users cannot delete secrets belonging to other projects or keys they do not have permission to modify.

**Why this priority**: Deleting an environment variable is a destructive operation that can break running services if performed by an unauthorized actor.

**Independent Test**: Attempt to delete a secret as an unassigned Project Developer (`403`), as a `RoleTier.OTHER` user without permission (`403`), and as a `RoleTier.OTHER` user with permission or as an assigned Project Developer / Admin (`200`).

**Acceptance Scenarios**:

1. **Given** an `ADMIN` user, **When** they delete any secret in any project, **Then** the deletion succeeds (`200 OK`).
2. **Given** a `PROJECT_DEVELOPER` assigned to Project A (and not Project B), **When** they delete a secret in Project A, **Then** it succeeds (`200 OK`); **When** they attempt to delete a secret in Project B, **Then** the API returns `HTTP 403 Forbidden`.
3. **Given** a `RoleTier.OTHER` user assigned to Project A, **When** they attempt to delete a key they do not have `WRITE` permission for, **Then** the API returns `HTTP 403 Forbidden`; **When** they have `WRITE` permission for that key (e.g., a key they created themselves), **Then** deletion succeeds (`200 OK`).

---

### User Story 3 - Real-Time SSE Broadcast & SDK Hot-Reload Removal (Priority: P3)

When a secret is deleted, the system publishes an SSE change event (`action="DELETE"`) so connected browser sessions and `dut-vault-sdk` clients are notified and remove/invalidate the deleted key from memory in real time.

**Why this priority**: Keeps all connected dashboards and running SDK processes synchronized without manual refreshes or restarts (Constitution Principle VII).

**Independent Test**: Subscribe to Vault SSE stream (or `InMemoryConfigStore`), delete a secret, and verify a `DELETE` event is emitted only to authorized subscribers.

**Acceptance Scenarios**:

1. **Given** a secret is deleted, **When** the database transaction commits, **Then** a Vault change event with `action="DELETE"` and `keys=[key]` is published via Redis Pub/Sub to authorized project subscribers.
2. **Given** the `SecretsTable` UI receives a `DELETE` SSE event, **When** the stream updates, **Then** the table query invalidates and removes the deleted key cleanly.

---

### Edge Cases

- What happens when the last secret in a scope is deleted? The scope itself may remain or be reflected with count `0` in `ScopeTabs` without breaking scope filtering.
- What happens when two different scopes (e.g., `Common` and `Production`) both have a key named `API_KEY` and only `Common/API_KEY` is deleted? Only `Common/API_KEY` is deleted; `Production/API_KEY` and any `key_permissions` for `API_KEY` remain intact.
- What happens when a `RoleTier.OTHER` user views the `SecretsTable`? Rows for which they lack delete permission should not crash; server-side `403` is always enforced regardless of UI state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide `DELETE /api/v1/vault/projects/{project_id}/secrets` accepting `scope_name` and `key` (via query parameters or request body — query parameters `scope_name` and `key` are preferred for standard HTTP `DELETE` compatibility).
- **FR-002**: Repository layer (`ISecretRepository` / `SqlSecretRepository`) MUST implement `delete_secret(project_id: str, scope_name: str, key: str) -> bool` without calling `session.commit()` internally (following Constitution Principle I).
- **FR-003**: Application layer MUST encapsulate deletion in `DeleteSecretUseCase` registered in Dishka `VaultProvider`, enforcing `ensure_project_access` and 3-tier RBAC (`ADMIN`, assigned `PROJECT_DEVELOPER`, or `OTHER` with `WRITE` key permission).
- **FR-004**: Deleting a secret MUST publish a Vault change event (`action="DELETE"`) via `VaultBroadcaster` after transaction/mutation so SSE listeners and `SecretsTable` stay synchronized.
- **FR-005**: Frontend `SecretsTable` MUST add a Delete (`Trash2`) action button per secret row and a confirmation dialog (`DeleteSecretDialog`) showing `scope_name` and `key` before invoking `useDeleteSecretMutation(projectId)`.
- **FR-006**: All new/updated backend and frontend code MUST pass `ruff check`, `ruff format`, `make api-types`, `pnpm typecheck`, `eslint`, and integration tests.

### Key Entities *(include if feature involves data)*

- **SecretEntity**: Existing Vault secret entity identified uniquely within a project by `(project_id, scope_id, key)`.
- **KeyPermissionEntity**: Existing granular key-level permission entity `(project_id, identity_id, secret_key, permission)`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authorized users can delete an environment variable from the UI in 2 clicks (Delete icon → Confirm) with immediate table and scope-count update.
- **SC-002**: 100% of unauthorized deletion attempts (unassigned project or `OTHER` user without `WRITE` permission) are rejected with `HTTP 403 Forbidden`.
- **SC-003**: Deleting a secret triggers real-time SSE propagation to connected UI clients within 5 seconds.

## Assumptions

- `DELETE /api/v1/vault/projects/{project_id}/secrets?scope_name=...&key=...` is used so Axios/HTTP proxies never strip a `DELETE` body.
- Deleting a secret removes the secret row and its cascaded `secret_versions` rows (`ondelete="CASCADE"` is already configured on `SecretVersionModel.secret_id`).
