# Feature Specification: Granular Key-Level Secret Permissions (Identity-to-Key ACL)

**Feature Branch**: `005-key-level-permissions`

**Created**: 2026-11-23

**Status**: Draft

**Input**: User description: "Ở nơi phân quyền cho .env, tôi ko hề quan tâm đến role, tôi yêu cầu ở đây chỉ cần phân quyền ai được get key gì thôi"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Identity-Based Key-Level Secret Retrieval (Priority: P1) 🎯 MVP

As an authenticated developer, machine client, or runtime service, I need the Vault to return only the specific secret keys that my identity has been explicitly granted permission to read, so that sensitive credentials remain strictly confidential and least-privilege access is enforced per identity regardless of roles.

**Why this priority**: Solves the core user requirement: eliminating coarse-grained role approximations and enforcing direct, granular "who gets what key" authorization across all secret reading operations.

**Independent Test**: Create two secrets (`DATABASE_URL`, `STRIPE_KEY`) in a project. Grant Identity A access only to `DATABASE_URL`. Request secrets as Identity A. Verify the response contains `DATABASE_URL` with its decrypted value, and `STRIPE_KEY` is completely omitted.

**Acceptance Scenarios**:

1. **Given** Identity A is granted read permission for `DATABASE_URL` and `APP_PORT` in Project X, **When** Identity A requests secrets for Project X, **Then** the response contains only `DATABASE_URL` and `APP_PORT` and their decrypted values.
2. **Given** a secret `STRIPE_SECRET_KEY` exists in Project X but has not been granted to Identity A, **When** Identity A requests secrets for Project X, **Then** `STRIPE_SECRET_KEY` is completely absent from the response payload.
3. **Given** Identity B has zero key permissions granted in Project X, **When** Identity B requests secrets for Project X, **Then** the response returns an empty dictionary of secrets or HTTP 403 (no secrets exposed).
4. **Given** an identity attempts to request a specific key directly by name (`key=STRIPE_SECRET_KEY`) without being granted access, **Then** the system immediately rejects the request with HTTP 403 Forbidden.

---

### User Story 2 - Key Permission Management (Grant, Revoke & List) (Priority: P2)

As a Project Administrator or Security Lead, I need to explicitly grant, revoke, and inspect key permissions for individual identities (user accounts or machine client IDs), so that I have complete control and auditability over which identity can access which configuration keys.

**Why this priority**: Administrators need an interface to manage the identity-to-key permission mappings dynamically without restarting services or modifying application code.

**Independent Test**: As an Administrator, grant Identity C permission for `PAYMENT_GATEWAY_KEY`. Verify Identity C can read the key. Then revoke the permission. Verify Identity C can no longer read the key.

**Acceptance Scenarios**:

1. **Given** an existing secret `API_SECRET` in Project X, **When** an Administrator grants access to Identity C, **Then** a key permission record is created and immediately active for subsequent queries.
2. **Given** Identity C holds permission for `API_SECRET`, **When** an Administrator revokes access from Identity C, **Then** the key permission is deleted and Identity C is immediately blocked from retrieving `API_SECRET`.
3. **Given** an Administrator queries permissions for Identity C in Project X, **When** the query executes, **Then** the system returns the exact list of secret keys Identity C is permitted to access.
4. **Given** an Administrator queries which identities have access to a specific key `DATABASE_URL`, **When** the query executes, **Then** the system returns all identities currently granted that key.

---

### User Story 3 - Key-Level Filtered SSE Event Streaming (Priority: P3)

As a connected client SDK instance listening to the real-time configuration event stream, I should only receive `secret_update` notifications when a secret key that my identity is authorized to access has changed, preventing information leakage about internal secret rotations that do not concern my service.

**Why this priority**: Preserves granular confidentiality on the real-time push channel, ensuring unauthorized key names and versions are not broadcast to clients who have no right to view them.

**Independent Test**: Connect Identity A (granted only `DATABASE_URL`) to the SSE stream. Update `STRIPE_KEY` on the Control Plane. Verify Identity A receives zero `secret_update` notifications. Then update `DATABASE_URL`. Verify Identity A immediately receives the `secret_update` event.

**Acceptance Scenarios**:

1. **Given** Identity A is connected to the project SSE stream and only has permission for `DATABASE_URL`, **When** `STRIPE_KEY` is modified, **Then** Identity A receives zero notifications.
2. **Given** Identity A is connected to the project SSE stream, **When** `DATABASE_URL` is modified, **Then** Identity A receives a `secret_update` event notifying that `DATABASE_URL` changed.

---

### Edge Cases

- **Non-existent Key Permission Grant**: If an Administrator attempts to grant access to a key that does not exist in the project, the system validates and rejects the request with a descriptive error.
- **Deleted Secret Cleanup**: When a secret key is deleted from a project, all associated key permissions for that key are automatically removed to prevent dangling grants.
- **Wildcard / Bulk Permission Grants**: An Administrator can optionally grant all keys in a project or scope to an identity using a wildcard pattern (`*`), or manage explicit key-by-key lists.
- **Identity Revocation**: If a client identity is revoked or disabled, all key read attempts immediately fail with HTTP 401/403.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Domain 1: Granular Key Permissions Management
- **FR-001**: System MUST support granting an identity (`identity_id`, representing either a user ID or machine client ID) read permission for a specific secret key within a project.
- **FR-002**: System MUST support revoking an identity's read permission for a specific secret key within a project.
- **FR-003**: System MUST provide an endpoint to list all keys permitted for a given identity in a project.
- **FR-004**: System MUST provide an endpoint to list all identities granted access to a given secret key in a project.
- **FR-005**: System MUST enforce that only Project Administrators or Project Owners can grant or revoke key permissions.

#### Domain 2: Identity-Based Secret Access Enforcement
- **FR-006**: Secret retrieval endpoints (`GET /api/v1/vault/projects/{project_id}/secrets`) MUST identify the caller identity (from authenticated token or identity header) and return ONLY the decrypted keys that the caller is explicitly permitted to read.
- **FR-007**: Role-based access rules (e.g. checking for "financial" or "common" role names) MUST be superseded by explicit identity-to-key permission checks.
- **FR-008**: If a caller identity has not been granted any keys in the project, the secret retrieval endpoint MUST return an empty configuration set without exposing any secret keys or values.
- **FR-009**: If an identity requests a specific key directly that has not been granted to that identity, the system MUST return HTTP 403 Forbidden.

#### Domain 3: Real-Time Stream Event Filtering
- **FR-010**: The Server-Sent Events stream (`GET /api/v1/vault/projects/{project_id}/stream`) MUST filter broadcast events based on the connected caller's granted keys, only transmitting `secret_update` events when at least one changed key is permitted for that caller.

### Key Entities

- **KeyPermission**: Represents a grant authorizing an identity to read a specific secret key. Contains `id`, `project_id`, `identity_id`, `identity_type` (`user` or `client`), `secret_key`, `granted_by`, and `granted_at`.
- **IdentitySecretAccess**: The resolved set of permitted secret keys for an identity within a project at runtime.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of secret retrieval responses contain exclusively keys that the caller identity is authorized to access; zero unauthorized keys or values are ever returned.
- **SC-002**: Key permission changes (grant or revoke) take effect instantaneously on the next request (< 50ms) without requiring service restarts or token re-issuance.
- **SC-003**: In-memory SDK hot-reload only receives and updates variables that the client identity is permitted to view.
- **SC-004**: Administrative key permission operations (grant, revoke, list) complete with a p95 latency under 100ms.

---

## Assumptions

- Caller identities are authenticated via existing authentication mechanisms (SSO JWT tokens, Gateway Client credentials `X-Client-Id`, or Actor ID headers).
- Project Administrators have full permission to configure secret values and assign key-level access to members and machine clients.
- Permissions are deny-by-default: an identity has zero access to any secret key until explicitly granted.
