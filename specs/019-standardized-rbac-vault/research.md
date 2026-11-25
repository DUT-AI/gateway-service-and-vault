# Research & Architectural Decisions: Standardized 3-Tier RBAC & Vault ACL

**Feature**: `019-standardized-rbac-vault` | **Date**: 2026-11-25

## 1. Role Tier Resolution from Pure SSO Claims

- **Decision**: Implement a deterministic `RoleTier` enum (`ADMIN`, `PROJECT_DEVELOPER`, `OTHER`) resolved from SSO token claims (`role_names` list + `role` string + `permissions` wildcard) in `core/security/roles.py`.
- **Rationale**:
  - Central DUT-AI Manage IdP issues tokens with `role_names` such as `["admin", "Trainer", "Project Developer", "Content"]`.
  - A user may hold multiple roles simultaneously (e.g. `["Trainer", "Project Developer"]`). Evaluating via highest-precedence order (`ADMIN` > `PROJECT_DEVELOPER` > `OTHER`) ensures predictable authorization without ambiguity.
  - Case-insensitive matching (`r.strip().lower()`) protects against formatting drift between IdP environments.
- **Alternatives Considered**:
  - Checking raw string `x_user_role` HTTP headers in routers: Rejected because clients can omit or spoof raw headers, and it caused the anonymous fallback bug in Vault.
  - Storing role mappings in a local `users` table: Rejected because Constitution Principle V strictly forbids local user persistence tables.

## 2. Project Membership Persistence (`project_members`)

- **Decision**: Introduce a dedicated `project_members` join table in the `gateway` bounded context storing `(id, project_id, user_id: int, added_by: int, created_at, updated_at)`.
- **Rationale**:
  - Both `Project Developer` and `Other Roles` (`Trainer`, `Content`) must only see and access projects they are explicitly assigned to.
  - Storing `user_id: int` directly (without a local `users` foreign key) satisfies Constitution Principle V (native integer user IDs, zero local user tables) while enabling fast SQL `JOIN` / `WHERE project_id IN (...)` filtering.
  - User profile details (name, email, avatar) for the Project Members UI modal are fetched via existing `IExternalUserDirectoryService` (`GET /api/v1/users/options`), which is already cached in Redis.
- **Alternatives Considered**:
  - Storing member IDs as a JSON array column on `projects`: Rejected because it prevents clean relational indexing, unique constraints, and clean SQL filtering when listing projects.

## 3. Vault Key-Level ACL vs Role Tier Interaction

- **Decision**: Decouple human SSO user access from machine client access cleanly in `GetSecretsByScopeUseCase`:
  - `ADMIN`: Full read/write access to all projects and all secret keys.
  - `PROJECT_DEVELOPER` (when member of project): Full read/write access to **all** secret keys within their assigned projects (`bypass_key_acl=True`).
  - `OTHER` (when member of project): Read/write access **only** to secrets they created (`created_by == str(user_id)` or `key_permissions` entry) or secrets explicitly granted to `str(user_id)` in `key_permissions`.
  - Machine Clients / SDKs (`X-Identity-Id` header without human SSO user context): Strictly governed by `key_permissions` (`bypass_key_acl=False`), preserving Zero-Trust least privilege for runtime services.
- **Rationale**:
  - Satisfies the user's requirement that Project Developers can seamlessly read all secrets in their assigned projects while Trainers/Content only see what they created or were assigned, AND preserves `dut-vault-sdk` machine-level key isolation.
- **Alternatives Considered**:
  - Auto-creating `key_permissions` rows for every key for every Project Developer: Rejected because newly added keys would require fan-out permission inserts for all developers on every secret creation.

## 4. Spoofing Protection & Test Compatibility

- **Decision**: When an endpoint is called with a human SSO Bearer token or `access_token` cookie, `get_current_user_payload` (or `get_optional_user_payload`) takes absolute precedence; client-supplied `X-Identity-Id` / `X-User-Role` headers cannot elevate a human user's privilege. Machine/integration test headers (`X-Identity-Id`) only apply when no human SSO token is present (for SDK / machine client calls).
- **Rationale**: Prevents privilege escalation via header injection (`X-User-Role: admin`) from browsers while keeping machine-to-machine SDK calls and integration tests working cleanly.
