# Implementation Plan: Web Phase 2 - Dynamic Vault Management & Key-Level ACL

**Branch**: `008-web-vault-acl` | **Date**: 2026-11-23 | **Spec**: [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/008-web-vault-acl/spec.md)

**Input**: Feature specification from `/specs/008-web-vault-acl/spec.md` and Phase 2 roadmap from `docs/WEB_ROADMAP.md`.

---

## Summary

Implement the frontend control plane for the Dynamic Vault Engine and Granular Key-Level Access Control (ACL). This replaces manual `.env` files with a secure, responsive web interface that organizes environment configurations by Scope, masks sensitive values by default with instant reveal/copy actions, allows creating and updating encrypted secrets with Zod validation, and provides an access control matrix to grant or revoke read permissions for individual secret keys to users from the central DUT-AI directory.

---

## Technical Context

**Language/Version**: TypeScript 5.x / Next.js 16.2.4 (App Router, React 19.2.4, Turbopack)  
**Primary Dependencies**: `@tanstack/react-query` v5, `axios`, `zod`, `react-hook-form`, `@hookform/resolvers`, `shadcn/ui` (Base UI primitives), `sonner`, `lucide-react`  
**Storage**: Backend PostgreSQL via async SQLAlchemy (`secrets`, `scopes`, `key_permissions` tables, encrypted with authenticated AES-256-GCM)  
**Testing**: `pnpm --prefix web typecheck`, `pnpm --prefix web build`, `uv run pytest`  
**Target Platform**: Modern desktop and mobile web browsers (Chrome, Firefox, Safari, Edge; responsive down to 320px)  
**Project Type**: Web feature module inside modular monolith architecture  
**Performance Goals**: <1.0s initial table load; <50ms mask/unmask toggle; <500ms optimistic permission mutation; zero layout shifts  
**Constraints**: 
- Zero plaintext `.env` files on disk (Constitution Principle VI).
- Secrets decrypted strictly on-demand in memory for authorized callers.
- User identifiers must strictly use native integer format (`id: number`) when interfacing with external user directory (Constitution Principle V).
- Offline contract synchronization via `web/src/types/api.generated.d.ts` (Constitution Principle IV).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Compliance Status | Justification / Notes |
|---|---|---|---|
| **I. Clean Architecture** | Pure domain layer without UI/framework leakage | **PASS** | Frontend logic resides purely in `web/src/features/vault/`; backend domain models remain untouched pure dataclasses. |
| **II. Modular Monolith** | Explicit boundary encapsulation | **PASS** | Vault web feature encapsulates services, hooks, and components in `web/src/features/vault/`. |
| **IV. Offline Type Sync** | Derived from OpenAPI schemas | **PASS** | Types use `Schema<"ScopeResponse">`, `Schema<"GetSecretsResponse">`, `Schema<"CreateSecretRequest">` from `web/src/types/api.ts`. |
| **V. Pure SSO & User Directory** | No local passwords, integer user IDs | **PASS** | User selection queries central directory `GET /api/v1/users/options`; uses `id: number` without string coercion workarounds. |
| **VI. Dynamic Vault & ACL** | AES-256-GCM encryption, granular key ACL | **PASS** | Secrets are encrypted on save; permission matrix grants/revokes individual secret keys. |
| **VII. Real-Time Hot-Reload** | Live config updates | **PASS (Prepared)** | Prepares data hooks and query invalidation foundations for Phase 3 SSE live streaming. |

---

## Project Structure

### Documentation (this feature)

```text
specs/008-web-vault-acl/
├── spec.md              # Feature specification and prioritized user stories
├── plan.md              # This architectural implementation plan
├── research.md          # Security masking, scope normalization, Zod validation
├── data-model.md        # Normalized UI types and form validation schemas
├── contracts/
│   └── vault-api.md     # API specifications for scopes, secrets, and permissions
├── quickstart.md        # Verification guide with automated and browser workflows
└── tasks.md             # Implementation checklist (/speckit-tasks output)
```

### Source Code Layout

```text
web/src/
├── features/
│   └── vault/
│       ├── types/
│       │   ├── index.ts                     # Schema<T> mappings & normalized types
│       │   └── form-schemas.ts              # Zod validation schema for secret creation
│       ├── services/
│       │   ├── vault-service.ts             # Axios HTTP client for scopes, secrets, permissions
│       │   └── user-directory-service.ts    # Axios HTTP client for GET /users/options
│       ├── hooks/
│       │   ├── use-vault-queries.ts         # useScopesQuery, useSecretsQuery, useSaveSecretMutation
│       │   ├── use-permissions-queries.ts   # useIdentityPermissionsQuery, grant & revoke mutations
│       │   └── use-user-options-query.ts    # useUserOptionsQuery
│       ├── components/
│       │   ├── scope-tabs.tsx               # Scope switcher tabs ("Tất cả", "Common", "Database", etc.)
│       │   ├── secrets-table.tsx            # Key-Value table with mask/unmask and copy actions
│       │   ├── secret-dialog.tsx            # Add/Edit encrypted secret modal dialog
│       │   ├── key-permission-matrix-modal.tsx # ACL modal with user dropdown and key checklist
│       │   ├── vault-view.tsx               # Main Vault container mounted in project workspace
│       │   └── index.ts                     # Public component exports
│       └── index.ts                         # Public feature exports (types, services, hooks, components)
└── features/projects/
    └── components/
        └── project-workspace-tabs.tsx       # Replaces Vault placeholder with <VaultView />
```

---

## Architectural Breakdown & User Stories

### Phase 1: Foundational Data Layer & Services
- Create `web/src/features/vault/types/` mapping `Scope`, `GetSecretsResponse`, `CreateSecretPayload`, `KeyPermission`, `UserOption`.
- Implement `vaultService` in `web/src/features/vault/services/vault-service.ts` with methods:
  - `listScopes(projectId)`
  - `getSecrets(projectId, scope?, key?)`
  - `createSecret(projectId, payload)`
  - `listPermissions(projectId, identityId)`
  - `grantPermission(projectId, payload)`
  - `revokePermission(projectId, identityId, secretKey)`
- Implement `userDirectoryService` in `web/src/features/vault/services/user-directory-service.ts` (`listUserOptions()`).
- Implement TanStack React Query hooks with structured query keys:
  - `VAULT_KEYS.scopes(projectId)`
  - `VAULT_KEYS.secrets(projectId)`
  - `VAULT_KEYS.permissions(projectId, identityId)`
  - `USER_KEYS.options()`

### Phase 2: User Story 1 (P1) - Scope Tabs & Encrypted Secret Table
- Implement `ScopeTabs`:
  - Renders horizontal tabs for all available project scopes + "Tất cả" (All).
  - Shows badge count of secrets in each scope.
- Implement `SecretsTable`:
  - Normalizes nested `GetSecretsResponse.scopes` into a searchable flat list.
  - Columns: Key (bold mono), Giá trị (masked by default, unmask toggle button, copy button), Nhóm (Badge), Thao tác (Sửa button).
  - Search input filtering by key name or scope name.
  - Skeletons and empty states when no secrets exist.
- Mount `VaultView` inside `ProjectWorkspaceTabs` under the "Biến môi trường (Vault)" tab.

### Phase 3: User Story 2 (P2) - Secret Creation & Edit Dialog
- Implement `createSecretSchema` in `form-schemas.ts` enforcing `^[A-Z0-9_]+$` key validation and non-empty values.
- Implement `SecretDialog`:
  - Scope selection: combobox/input allowing existing scope selection or custom scope name creation.
  - Key input with auto-formatting to uppercase.
  - Value input with show/hide password toggle.
  - Submit button with spinner loading state.
  - Success feedback via Sonner toast and automatic cache invalidation.

### Phase 4: User Story 3 (P3) - Granular Key Permissions Matrix Modal
- Implement `KeyPermissionMatrixModal`:
  - User selector dropdown querying `useUserOptionsQuery()`.
  - Checkbox matrix of all project secret keys.
  - Toggling checkbox immediately calls `useGrantPermissionMutation` or `useRevokePermissionMutation`.
  - Optimistic UI updates with Sonner toast feedback and error rollback.

### Phase 5: Verification & Polish
- Full typecheck: `pnpm --prefix web typecheck` (0 errors).
- Full production build: `pnpm --prefix web build` (successful compilation).
- Backend test validation: `uv run pytest` (46/46 passed).
- Responsive testing across desktop, tablet, and mobile breakpoints.
