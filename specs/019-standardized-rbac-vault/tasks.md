---

description: "Task list for Standardized 3-Tier Role-Based Access Control & Vault ACL"
---

# Tasks: Standardized 3-Tier Role-Based Access Control & Vault ACL

**Input**: Design documents from `specs/019-standardized-rbac-vault/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/rbac-api.md`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story, strictly adhering to Constitution v2.3.0 (Clean Architecture, Pure SSO, Thin Presentation Layer).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup & Role Classification Infrastructure

**Purpose**: Establish the 3-tier `RoleTier` model (`ADMIN`, `PROJECT_DEVELOPER`, `OTHER`) from SSO claims across backend and frontend.

- [x] T001 [P] Create `RoleTier` enum, `UserContext` dataclass, and `resolve_user_role_tier()` helper in `core/security/roles.py`
- [x] T002 [P] Add `get_current_user_context`, `get_optional_user_context`, and `require_role_tier(*allowed_tiers)` dependencies in `core/security/deps.py`
- [x] T003 [P] Compute and expose `roleTier`, `isAdmin`, `isDeveloper`, `isOtherRole` in `web/src/contexts/auth-context.tsx` and `web/src/features/auth/types/index.ts`

---

## Phase 2: Foundational (Project Membership Domain & Persistence)

**Purpose**: Core `project_members` persistence and Clean Architecture use cases required before role enforcement.

- [x] T004 Create `ProjectMemberEntity` pure dataclass in `modules/gateway/domain/entities.py`
- [x] T005 Define `IProjectMemberRepository` interface in `modules/gateway/domain/interfaces.py`
- [x] T006 Create `ProjectMemberModel` in `modules/gateway/models/member.py`, export in `modules/gateway/models/__init__.py`, and wire relationship in `modules/gateway/models/project.py`
- [x] T007 Generate and apply Alembic migration for `project_members` table in `alembic/versions/`
- [x] T008 Implement `SqlProjectMemberRepository` in `modules/gateway/repository/project_member_repository.py` (no `.commit()` calls, Single Aggregate Root)
- [x] T009 Add `ProjectMemberCreateRequest` and `ProjectMemberResponse` schemas in `modules/gateway/dtos/gateway_dtos.py`
- [x] T010 Implement `AddProjectMemberUseCase`, `RemoveProjectMemberUseCase`, `ListProjectMembersUseCase`, `CheckProjectMembershipUseCase` in `modules/gateway/use_cases/member_use_cases.py`, export in `modules/gateway/use_cases/__init__.py`, and register in `modules/gateway/di.py`

**Checkpoint**: Foundation ready — 3-tier role resolution and project membership infrastructure operational.

---

## Phase 3: User Story 1 - System Administrator Governance & Membership Management (Priority: P1) 🎯 MVP

**Goal**: Admins have unrestricted governance over all projects, upstream services, quotas, permissions matrix, and can assign/remove project members.

**Independent Test**: Log in with `admin` role -> Create/delete projects, assign developers/trainers to projects, view all Vault secrets, grant/revoke key permissions.

- [x] T011 [US1] Create `apps/api/routers/gateway/members.py` (`GET/POST/DELETE /projects/{project_id}/members`) protected by `require_role_tier(RoleTier.ADMIN)` and register in `apps/api/routers/gateway/__init__.py`
- [x] T012 [US1] Enforce `require_role_tier(RoleTier.ADMIN)` on administrative endpoints in `apps/api/routers/gateway/projects.py` (create/delete), `services.py` (global upstream service CRUD & quota updates), and `apps/api/routers/vault/permissions.py` (grant/revoke)
- [x] T013 [P] [US1] Create `web/src/features/gateway/services/member-service.ts` and `web/src/features/gateway/hooks/use-member-queries.ts`
- [x] T014 [US1] Create `ProjectMembersModal` component in `web/src/features/gateway/components/project-members-modal.tsx` and integrate into project workspace for Admins

**Checkpoint**: User Story 1 (MVP) complete — Admins can manage memberships and govern all resources.

---

## Phase 4: User Story 2 - Project Developer Workspace & Full-Project Secret Access (Priority: P2)

**Goal**: Project Developers only see assigned projects, read all secrets in assigned projects, and manage virtual keys / mTLS clients for assigned projects.

**Independent Test**: Log in as `Project Developer` -> Verify only assigned projects appear (unassigned returns 403) -> Verify all secrets in assigned project are readable -> Verify creating projects or altering quotas returns 403.

- [x] T015 [US2] Update `ListProjectsUseCase` in `modules/gateway/use_cases/project_use_cases.py` and `IProjectRepository` / `SqlProjectRepository` to filter projects by `user_id` membership when user is not `ADMIN`
- [x] T016 [US2] Enforce project membership & role checks (`ADMIN` or `PROJECT_DEVELOPER`) in `apps/api/routers/gateway/projects.py` (get detail), `clients.py`, `keys.py`, `services.py` (project services list), and `audit.py`
- [x] T017 [US2] Update `GetSecretsByScopeUseCase` in `modules/vault/use_cases/get_secrets_by_scope.py` to support `bypass_key_acl: bool = False`, and update `apps/api/routers/vault/secrets.py` & `stream.py` so `PROJECT_DEVELOPER` (with project membership) reads all project secrets & SSE events
- [x] T018 [US2] Update frontend UI in `web/src/features/gateway/` and `web/src/features/vault/` to hide Admin-only controls ("Tạo dự án", "Quản lý thành viên", "Cấu hình Quota", "Phân quyền truy cập", global Services nav) from `PROJECT_DEVELOPER`

**Checkpoint**: User Story 2 complete — Project Developers operate smoothly inside assigned projects.

---

## Phase 5: User Story 3 - Project-Scoped & Key-Filtered Access for Other Roles (Priority: P3)

**Goal**: Other roles (`Trainer`, `Content`, etc.) see only assigned projects, view project details, and read/manage only secrets they created or were explicitly granted in `key_permissions`.

**Independent Test**: Log in as `Trainer` or `Content` -> Verify only assigned projects appear -> Create secret and verify it is visible -> Verify ungranted secrets created by others are hidden -> Verify virtual key/client mutations return 403.

- [x] T019 [US3] Enforce `403 Forbidden` for `RoleTier.OTHER` on mutating gateway endpoints in `apps/api/routers/gateway/clients.py`, `keys.py`, and `services.py`
- [x] T020 [US3] Ensure `CreateSecretUseCase` in `modules/vault/use_cases/create_secret.py` and `apps/api/routers/vault/secrets.py` auto-grant `key_permissions` to `str(user_id)` when `RoleTier.OTHER` creates a secret, and `GET /secrets` + `GET /stream` strictly filter by `key_permissions`
- [x] T021 [US3] Update frontend UI for `RoleTier.OTHER` (`isOtherRole`) to hide Keys/mTLS tabs, SDK quickstart, and permission matrix controls while permitting assigned project detail viewing and secret creation/viewing for their own/assigned keys

**Checkpoint**: User Story 3 complete — All 3 role tiers strictly enforced across Backend and Frontend.

---

## Phase 6: Verification, Type Sync & Polish

**Purpose**: Synchronize API types, verify architecture purity, and run end-to-end automated tests.

- [x] T022 [P] Run `make api-types` to synchronize `ProjectMemberResponse` and `ProjectMemberCreateRequest` into `web/src/types/api.ts`
- [x] T023 Write comprehensive integration test suite `tests/integration/test_rbac_3_tier.py` covering `ADMIN`, `PROJECT_DEVELOPER`, `OTHER`, Project Membership isolation, anti-spoofing headers, and Vault key filtering
- [x] T024 Run full quality gates: `uv run ruff check --fix && uv run ruff format`, `make check`, and `uv run pytest` (including `tests/test_clean_architecture_purity.py`)

---

## Dependencies & Execution Order

- **Phase 1 (Setup)**: Independent — starts immediately (`T001`, `T002`, `T003` in parallel).
- **Phase 2 (Foundational)**: Depends on Phase 1 (`T001`/`T002`); blocks all user stories.
- **Phase 3 (US1 - Admin)**: Depends on Phase 2.
- **Phase 4 (US2 - Project Developer)**: Depends on Phase 2 (and uses membership endpoints from US1 for testing).
- **Phase 5 (US3 - Other Roles)**: Depends on Phase 2 & US2's membership guards.
- **Phase 6 (Verification)**: Depends on Phases 3, 4, 5.

## Implementation Strategy

- **MVP First**: Complete Phases 1–3 to deliver `RoleTier` resolution + `project_members` management for Admins.
- **Incremental Delivery**: Add Phase 4 (`Project Developer` project-scoped full secret access) -> Phase 5 (`Other Roles` key-filtered access) -> Phase 6 (Full test & type-check verification).
