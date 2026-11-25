# Implementation Plan: Self-Service mTLS Client & Key UX + Ownership Scoping

**Branch**: `020-mtls-client-ux-scoping` | **Date**: 2026-11-25 | **Spec**: [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/020-mtls-client-ux-scoping/spec.md)

**Input**: Feature specification from `/specs/020-mtls-client-ux-scoping/spec.md`

## Summary

Enforce strict ownership isolation for mTLS Clients (`registered_clients`) and upgrade the "Thiết bị & Client mTLS" UX:
1. **Backend Ownership Scoping**:
   - `POST /gateway/clients`: Always sets `owner_id = str(user_ctx.user_id)` from the verified SSO token for all callers (`ADMIN` & `PROJECT_DEVELOPER`), preventing spoofing or creating certs on behalf of others.
   - `GET /gateway/clients`: `ADMIN` sees all system clients; `PROJECT_DEVELOPER` sees only their own clients (`list_by_owner_id`).
   - `POST /gateway/clients/{client_id}/revoke`: `ADMIN` can revoke any client; `PROJECT_DEVELOPER` can only revoke their own (`403 Forbidden` otherwise).
   - Project Virtual Keys (`GET/POST /projects/{id}/keys`, `POST /keys/{id}/revoke`) remain scoped to Project Membership for Developers and unrestricted for Admins.
2. **Frontend UX Upgrades**:
   - `ClientsTable`: Resolve `owner_id` via `useUserOptionsQuery` to display SSO owner avatar, name, and email instead of raw IDs. Add Admin scope tabs ("Tất cả hệ thống" vs "Thiết bị của tôi") + Type/Status filters.
   - `CertDownloadDialog`: Add clear post-download callout guiding users to the **Virtual Keys** tab inside their Project detail page (`/projects`) to generate project-scoped API keys.

## Technical Context

**Language/Version**: Python 3.12+ (Backend), TypeScript / React 19 / Next.js 16 (Frontend)
**Primary Dependencies**: FastAPI, Dishka IoC, SQLAlchemy 2.0, Pydantic v2, TanStack Query, Tailwind CSS v4, shadcn/ui
**Storage**: PostgreSQL (`registered_clients`, `virtual_access_keys`) — zero schema migration required (`owner_id` column and `list_by_owner_id` already exist!)
**Testing**: Pytest (unit + integration + purity gates), TypeScript `tsc --noEmit`
**Target Platform**: Linux Docker / macOS local dev
**Project Type**: Modular Monolith Web Application
**Constraints**: Pure SSO (`UserContext`), Thin Presentation Layer (all ownership checks inside Use Cases, zero repositories injected in routers).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Clean Architecture & Thin Presentation Layer)**: **PASS** — Ownership validation (`ClientOwnershipDeniedError`) lives inside `RevokeClientUseCase` and `ListRegisteredClientsUseCase`; `clients.py` router remains a thin HTTP adapter.
- **Principle IV (Offline Contract & Type Sync)**: **PASS** — If `RegisterClientRequest.owner_id` becomes optional, run `make api-types` to sync `web/src/types/api.generated.d.ts`.
- **Principle V (Pure SSO)**: **PASS** — `owner_id` is derived strictly from verified SSO `UserContext.user_id`; owner display profiles come from `IExternalUserDirectoryService` (`/api/v1/users/options`).

## Project Structure

### Documentation (this feature)

```text
specs/020-mtls-client-ux-scoping/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── clients-ux-api.md
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
modules/gateway/
├── dtos/gateway_dtos.py                    # UPDATED: Make RegisterClientRequest.owner_id optional
└── use_cases/
    ├── exceptions.py                       # UPDATED: Add ClientOwnershipDeniedError
    ├── list_registered_clients.py          # UPDATED: Scope by owner_id when not admin
    └── revoke_client.py                    # UPDATED: Enforce ownership check when not admin

apps/api/routers/gateway/
└── clients.py                              # UPDATED: Pass user_ctx.user_id & is_admin to use cases; map 403

web/src/features/clients/components/
├── clients-table.tsx                       # UPDATED: SSO owner avatar/name/email + Admin scope tabs
└── cert-download-dialog.tsx                # UPDATED: Next-step guidance link to /projects Virtual Keys

tests/integration/
└── test_client_ownership_scoping.py        # NEW: Verify cross-user isolation, spoofing prevention, and admin governance
```

## Complexity Tracking

No constitutional violations. Zero new database tables or migrations needed.
