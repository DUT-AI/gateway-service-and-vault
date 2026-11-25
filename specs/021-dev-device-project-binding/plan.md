# Implementation Plan: Regular Dev Device Self-Registration & Project Developer Key Binding

**Branch**: `021-dev-device-project-binding` | **Date**: 2026-11-25 | **Spec**: [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/021-dev-device-project-binding/spec.md)

**Input**: Feature specification from `/specs/021-dev-device-project-binding/spec.md`

## Summary

Enable the complete 3-tier device-to-project key binding workflow:
1. **Regular Dev (`Tier 3 / OTHER`)**:
   - Can access `/clients` ("Thiết bị & Client") to self-register personal `USER_DEVICE` mTLS certificates (`APP_SERVER` returns `403 Forbidden`), view, and revoke **only** their own devices.
   - Inside assigned projects, can view the **Virtual Keys** tab in **read-only** mode, seeing only Virtual Keys bound to their own devices.
2. **Project Developer (`Tier 2`)**:
   - Inside assigned projects, can call `GET /gateway/projects/{project_id}/available-clients` to view active mTLS devices belonging to **members of that project (`project_members`)** (plus Admin-owned shared clients if applicable) and bind Virtual Access Keys for them via `GenerateKeyModal` (with SSO owner name/email/avatar).
3. **Admin (`Tier 1`)**:
   - Full governance across all clients, project available clients, and all Virtual Keys.

## Technical Context

**Language/Version**: Python 3.12+ (Backend), TypeScript / React 19 / Next.js 16 (Frontend)
**Primary Dependencies**: FastAPI, Dishka IoC, SQLAlchemy 2.0, Pydantic v2, TanStack Query, Tailwind CSS v4
**Storage**: PostgreSQL (`registered_clients`, `project_members`, `virtual_access_keys`) — zero schema changes needed
**Testing**: Pytest (unit + integration + purity gates), TypeScript `tsc --noEmit`
**Constraints**: Pure SSO, Thin Presentation Layer (all cross-aggregate queries orchestrated in Use Cases, zero repositories injected in routers).

## Constitution Check

- **Principle I (Clean Architecture & Thin Presentation Layer)**: **PASS** — `ListProjectAvailableClientsUseCase` and `ListProjectVirtualKeysUseCase` encapsulate all project-member-to-client filtering in the Use Case layer; routers remain thin HTTP adapters.
- **Principle IV (Offline Contract & Type Sync)**: **PASS** — `make api-types` will sync any new/updated endpoints to `web/src/types/api.generated.d.ts`.
- **Principle V (Pure SSO & 3-Tier RBAC)**: **PASS** — Enforces `RoleTier.OTHER` `USER_DEVICE`-only rule and Project Membership scoping.
- **Principle VIII (Self-Issued mTLS Ownership)**: **PASS** — `owner_id` remains strictly locked to `str(user_ctx.user_id)` on `POST /clients` for all 3 tiers.

## Project Structure

### Documentation (this feature)

```text
specs/021-dev-device-project-binding/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── device-project-binding-api.md
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
modules/gateway/
├── domain/interfaces.py                         # UPDATED: Add list_by_owner_ids() to IRegisteredClientRepository
├── repository/registered_client_repository.py   # UPDATED: Implement list_by_owner_ids()
└── use_cases/
    ├── list_project_available_clients.py        # NEW: Return active clients owned by project members (or all for Admin)
    ├── list_virtual_keys.py                     # UPDATED: Support filtering by owner_id for Tier 3 read-only view
    └── __init__.py & di.py                      # UPDATED: Export & bind ListProjectAvailableClientsUseCase

apps/api/routers/gateway/
├── clients.py                                   # UPDATED: Allow RoleTier.OTHER on /clients; block APP_SERVER for OTHER
└── keys.py                                      # UPDATED: Add GET /projects/{id}/available-clients; allow OTHER read-only on GET /projects/{id}/keys

web/src/
├── components/layout/app-shell.tsx              # UPDATED: Show "Thiết bị & Client" (/clients) in sidebar for isOtherRole
├── features/clients/components/
│   └── register-client-dialog.tsx               # UPDATED: Lock client_type to USER_DEVICE when isOtherRole
├── features/projects/components/
│   └── project-workspace-tabs.tsx               # UPDATED: Show Virtual Keys tab (read-only) for isOtherRole
└── features/keys/
    ├── services/keys-service.ts                 # UPDATED: Fetch /projects/{id}/available-clients
    ├── hooks/use-keys-queries.ts                # UPDATED: useProjectAvailableClientsQuery
    └── components/
        ├── virtual-keys-view.tsx                # UPDATED: Hide Generate/Revoke actions when isOtherRole
        └── generate-key-modal.tsx               # UPDATED: Use project available clients + show owner avatar/name/email
```

## Complexity Tracking

No constitutional violations. Zero new database migrations required.
