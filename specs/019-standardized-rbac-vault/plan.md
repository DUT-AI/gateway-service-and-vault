# Implementation Plan: Standardized 3-Tier Role-Based Access Control & Vault ACL

**Branch**: `019-standardized-rbac-vault` | **Date**: 2026-11-25 | **Spec**: [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/019-standardized-rbac-vault/spec.md)

**Input**: Feature specification from `/specs/019-standardized-rbac-vault/spec.md`

## Summary

Replace ad-hoc header checks and hardcoded role assumptions with a formal, end-to-end 3-tier RBAC + Project Membership + Key-Level ACL architecture derived strictly from verified DUT-AI SSO tokens:
1. **`admin` (Tier 1)**: Unrestricted governance over all projects, project memberships, upstream services, quotas, virtual keys, key-permission matrix, and all Vault secrets.
2. **`Project Developer` (Tier 2)**: Project-membership scoped access; can view assigned projects, read/create/update **all** secrets within assigned projects, and manage virtual keys / mTLS clients for assigned projects.
3. **`Other Roles` (`Trainer`, `Content`, etc. - Tier 3)**: Project-membership scoped access; can view assigned projects, create secrets (auto-granted to creator), and read **only** secrets they created or were explicitly granted via `key_permissions`. Blocked (`403 Forbidden`) from administrative or gateway key mutations.

## Technical Context

**Language/Version**: Python 3.12+ (Backend), TypeScript / React 19 / Next.js 16 (Frontend)
**Primary Dependencies**: FastAPI, Dishka IoC, SQLAlchemy 2.0 (asyncpg), Alembic, Pydantic v2, TanStack Query, Axios, Tailwind CSS v4, shadcn/ui
**Storage**: PostgreSQL (`project_members`, `key_permissions`, `projects`, `secrets`) + Redis (SSO user directory cache & SSE Pub/Sub)
**Testing**: Pytest (unit + integration + purity gates), Vitest / TypeScript `tsc --noEmit`
**Target Platform**: Linux Docker / macOS local dev
**Project Type**: Modular Monolith Web Application (FastAPI API + Next.js Web)
**Constraints**: Pure SSO (zero local `users` table), native integer `user_id: int`, Thin Presentation Layer (zero repositories injected in routers).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Clean Architecture & Thin Presentation Layer)**: **PASS** — `ProjectMemberEntity` is a pure dataclass; `IProjectMemberRepository` and `SqlProjectMemberRepository` isolate persistence; routers in `apps/api/routers/gateway/members.py` and `projects.py` inject only Use Cases via Dishka.
- **Principle II (Modular Monolith & Dishka IoC)**: **PASS** — `GatewayProvider` binds `IProjectMemberRepository` and membership use cases cleanly in `Scope.REQUEST`.
- **Principle IV (Offline Contract & Type Sync)**: **PASS** — New Pydantic schemas for project members will be synced to `web/src/types/api.ts` via `make api-types`.
- **Principle V (Pure SSO & Native Integer User IDs)**: **PASS** — Zero local user tables; `project_members.user_id` and `added_by` are native `int`; identity & role tiers are extracted exclusively from verified SSO tokens.
- **Principle VI (Dynamic Vault & Granular Key-Level Access Control)**: **PASS** — Machine clients and `OTHER` roles strictly enforce `key_permissions` ACL; `PROJECT_DEVELOPER` and `ADMIN` operate within their defined project/system boundaries.
- **Principle VII (Real-Time SSE Filtering)**: **PASS** — `/vault/projects/{id}/stream` enforces the exact same role tier + membership + key-level filtering rules.

## Project Structure

### Documentation (this feature)

```text
specs/019-standardized-rbac-vault/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── rbac-api.md
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
core/security/
├── roles.py             # NEW: RoleTier enum, UserContext, resolve_user_role_tier()
└── deps.py              # UPDATED: get_current_user_context, require_roles(), get_optional_user_context

alembic/versions/
└── xxxx_add_project_members_table.py  # NEW: Migration for project_members

modules/gateway/
├── domain/
│   ├── entities.py      # UPDATED: ProjectMemberEntity
│   └── interfaces.py    # UPDATED: IProjectMemberRepository
├── models/
│   ├── member.py        # NEW: ProjectMemberModel
│   └── project.py       # UPDATED: members relationship
├── repository/
│   └── project_member_repository.py   # NEW: SqlProjectMemberRepository
├── dtos/
│   └── gateway_dtos.py  # UPDATED: ProjectMemberCreateRequest, ProjectMemberResponse
├── use_cases/
│   ├── member_use_cases.py  # NEW: Add/Remove/List/CheckProjectMemberUseCases
│   └── project_use_cases.py # UPDATED: Filter ListProjectsUseCase by user_id & RoleTier
└── di.py                # UPDATED: Register IProjectMemberRepository & member use cases

modules/vault/use_cases/
├── create_secret.py         # UPDATED: Auto-grant key permission to creator identity
└── get_secrets_by_scope.py  # UPDATED: Support bypass_key_acl for ADMIN & PROJECT_DEVELOPER

apps/api/routers/
├── gateway/
│   ├── __init__.py      # UPDATED: Include members router
│   ├── members.py       # NEW: Project membership endpoints (ADMIN only)
│   ├── projects.py      # UPDATED: Enforce RoleTier & Project Membership checks
│   ├── clients.py       # UPDATED: Enforce ADMIN / PROJECT_DEVELOPER + Membership
│   ├── keys.py          # UPDATED: Enforce ADMIN / PROJECT_DEVELOPER + Membership
│   ├── services.py      # UPDATED: Enforce ADMIN for global services/quotas, Membership for read
│   └── audit.py         # UPDATED: Enforce Membership / ADMIN
└── vault/
    ├── secrets.py       # UPDATED: Resolve UserContext, check membership, pass bypass_key_acl
    ├── permissions.py   # UPDATED: Enforce ADMIN for grant/revoke
    └── stream.py        # UPDATED: Enforce RoleTier + Membership + Key-level SSE filtering

web/src/
├── contexts/auth-context.tsx               # UPDATED: Expose roleTier, isAdmin, isDeveloper, isOtherRole
├── features/gateway/
│   ├── services/member-service.ts          # NEW: API client for project members
│   ├── hooks/use-member-queries.ts         # NEW: TanStack Query hooks for members
│   └── components/project-members-modal.tsx # NEW: Admin modal to assign/remove project members
└── features/vault/ & app/                  # UPDATED: Role-aware UI controls & navigation guards
```

**Structure Decision**: Extends the existing modular monolith (`core/security`, `modules/gateway`, `modules/vault`, `apps/api/routers`) and feature-sliced Next.js frontend (`web/src/features/`), maintaining strict adherence to Constitution v2.3.0.

## Complexity Tracking

No constitutional violations. All patterns follow existing Dishka IoC, Repository Isolation, and Thin Presentation Layer standards.
