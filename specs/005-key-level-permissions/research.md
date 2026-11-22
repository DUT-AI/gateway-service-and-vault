# Phase 0: Research & Technical Decisions - Granular Key-Level Permissions

**Feature**: `005-key-level-permissions`  
**Date**: 2026-11-23  
**Status**: Completed  

---

## 1. Permission Model: Key Allowlist (ACL) vs. Scope RBAC vs. Attribute-Based Access Control (ABAC)

### Context
The user explicitly specified: *"Ở nơi phân quyền cho .env, tôi ko hề quan tâm đến role, tôi yêu cầu ở đây chỉ cần phân quyền ai được get key gì thôi"*.
The previous implementation grouped secrets into static roles (`financial` vs `common`), which is too coarse and does not fit user expectations.

### Decision
Implement an **Explicit Identity-to-Key Allowlist (Key-Level Access Control List / ACL)**.

### Rationale
- **Direct Matching with User Intent**: The core question is: *"Can Identity X read Key Y?"*. A direct mapping table `(project_id, identity_id, secret_key)` provides unambiguous, fine-grained access control with zero role indirection.
- **Principle of Least Privilege**: Each developer, service, or machine client (`identity_id`) receives grants ONLY for the exact keys it needs to execute. A payment microservice gets `STRIPE_KEY` and `DB_URL`; a frontend SSR container gets `NEXT_PUBLIC_API_URL` and `AUTH_SECRET`; a data engineer gets `ANALYTICS_DB_URL`.
- **Deny-by-Default Invariant**: An identity with no granted keys receives an empty configuration payload (`{}`). No secrets are leaked by default.
- **Support for Wildcard Grants**: To avoid cumbersome administrative overhead for small teams or general dev environments, administrators can grant `*` (all keys in project) when appropriate.
- **Alternatives Considered**:
  - *Role-Based Access Control (RBAC)*: Coarse-grained; leads to "role explosion" (e.g. `billing_dev`, `billing_readonly`, `dev_frontend_tier2`) when different services need slightly different key combinations.
  - *Attribute-Based Access Control (ABAC)*: High evaluation complexity and opaque policy rules; overkill for key-value pair access authorization.

---

## 2. Caller Identity Identification Strategy

### Context
How does the Vault Control Plane reliably determine "Who" is requesting the configuration keys across developer laptops, automated scripts, and microservice containers?

### Decision
Extract the caller identity (`identity_id`) from request headers and authentication tokens with a standardized precedence chain:
1. **Gateway Authenticated Client**: `X-Client-Id` (authenticated via mTLS or client credentials).
2. **SSO / JWT Subject**: `sub` claim or `user_id` from Bearer token.
3. **Explicit Identity Header**: `X-Identity-Id` (for development / CLI runner environments).

### Rationale
- Decouples authorization from the specific authentication transport (supports both machine-to-machine mTLS clients and developer SSO tokens).
- Compatible with existing `apps/api/routers/gateway_router.py` and `modules/gateway/domain/entities.py`.

---

## 3. Database Schema & Indexing for Key Permissions

### Context
Every secret retrieval query must evaluate key-level permissions quickly (< 10ms) without creating query bottlenecks.

### Decision
Create a dedicated `key_permissions` table:
```sql
CREATE TABLE key_permissions (
    id VARCHAR(26) PRIMARY KEY,
    project_id VARCHAR(26) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    identity_id VARCHAR(100) NOT NULL,
    identity_type VARCHAR(20) NOT NULL DEFAULT 'client',
    secret_key VARCHAR(100) NOT NULL,
    granted_by VARCHAR(100) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_project_identity_key UNIQUE (project_id, identity_id, secret_key)
);
CREATE INDEX ix_key_permissions_lookup ON key_permissions(project_id, identity_id);
```

### Rationale
- The composite index `(project_id, identity_id)` ensures index-only scans when fetching permitted keys for a caller.
- Cascade deletion ensures when a project is removed, associated permissions are cleaned up automatically.
- Unique constraint prevents duplicate grant records.

---

## 4. SSE Stream Filtering with Key-Level Permissions

### Context
When a secret is updated, the Control Plane broadcasts `secret_update` containing `changed_keys: list[str]`. How do connected clients receive only events for keys they can read?

### Decision
On the SSE stream endpoint `GET /api/v1/vault/projects/{project_id}/stream`:
1. Authenticate caller identity (`identity_id`).
2. Resolve caller's permitted keys set `P = {k1, k2, ...}` from database or cache.
3. When Redis Pub/Sub publishes an event with `changed_keys`:
   - Compute intersection: `permitted_changed = set(changed_keys) & P`.
   - If `*` in `P` or `permitted_changed` is non-empty:
     - Yield `secret_update` containing only `changed_keys = list(permitted_changed)`.
   - Otherwise, suppress the event entirely (zero leakage).
