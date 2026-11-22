---
description: "Task list for SSO-Only Authentication & External User Directory feature implementation"
---

# Tasks: SSO-Only Authentication & External User Directory

**Input**: Design documents from `/specs/006-sso-auth-external-users/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/external-users-api.md`, `quickstart.md`  
**Tests**: Included as specified in spec criteria and quality gates.  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Exact file paths included in all task descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Database schema adjustment and baseline cleanup for SSO-only identity

- [X] T001 Create Alembic migration in `migrations/versions/004_drop_local_users_auth.py` removing password hash constraints from `users` table or marking it obsolete
- [X] T002 Apply Alembic migration `004_drop_local_users_auth` to running PostgreSQL database via `uv run alembic upgrade head`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain entities, DTOs, protocols, and HTTP client that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Define pure domain entities `ExternalUserOptionEntity`, `ExternalUserDetailEntity`, and `SsoSessionEntity` in `modules/identity/domain/entities.py` with `id: int` (zero framework imports)
- [X] T004 [P] Define Pydantic v2 response schemas `UserOptionResponse` and `UserDetailResponse` with `id: int` in `modules/identity/dtos/user_dtos.py`
- [X] T005 [P] Define interface protocol `IExternalUserDirectoryService` in `modules/identity/domain/interfaces.py` with methods `get_user_options` and `get_user_by_id`
- [X] T006 Implement `ExternalUserDirectoryService` in `modules/identity/services/external_user_service.py` integrating with `https://manage.dutai.io.vn/api/v1/users/options` and `https://manage.dutai.io.vn/api/v1/users/{id}` using async HTTPX with connection pooling and timeouts
- [X] T007 Register `ExternalUserDirectoryService` in Dishka `IdentityProvider` in `modules/identity/di.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Pure SSO Authentication Without Local User Accounts (Priority: P1) 🎯 MVP

**Goal**: Authenticate users exclusively via DUT-AI SSO (`manage.dutai.io.vn`), return profile with native integer ID (`id: int`), and eliminate local user password management.

**Independent Test**: Send request to `/api/v1/auth/me` with valid SSO access token -> verify user profile is returned with `id: 1` as native integer without querying local user database. Attempting local password registration is disabled.

### Tests for User Story 1

- [X] T008 [P] [US1] Create integration test in `tests/integration/test_sso_only_auth.py` validating SSO-only authentication, `/api/v1/auth/me` returning native integer ID, and rejection of invalid tokens

### Implementation for User Story 1

- [X] T009 [US1] Refactor `core/security/deps.py` to validate SSO token, extract `int(payload["sub"])` directly as native integer, and verify with `DutAiSsoService` without local database lookups
- [X] T010 [US1] Refactor `apps/api/routers/auth_router.py` to remove local `/register` and `/login` endpoints, keeping `/sso-login`, `/me`, and `/logout` strictly through SSO

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently (MVP ready!)

---

## Phase 4: User Story 2 - Remote User Directory Listing (`/users/options`) (Priority: P2)

**Goal**: Allow callers to retrieve user options list (`/users/options`) directly from the central directory for project ownership and permissions assignment.

**Independent Test**: Call `GET /api/v1/users/options` with valid SSO token -> verify list of user options with `id: int`, `name`, `email`, and `avatar_url` is returned.

### Tests for User Story 2

- [X] T011 [P] [US2] Create unit test in `tests/unit/test_get_user_options_use_case.py` testing `GetUserOptionsUseCase` with mocked directory service

### Implementation for User Story 2

- [X] T012 [P] [US2] Implement `GetUserOptionsUseCase` in `modules/identity/use_cases/get_user_options.py` and export in `modules/identity/use_cases/__init__.py`
- [X] T013 [US2] Register `GetUserOptionsUseCase` in Dishka `IdentityProvider` in `modules/identity/di.py`
- [X] T014 [US2] Create `apps/api/routers/user_router.py` with endpoint `GET /api/v1/users/options` and register router in `apps/api/main.py`

**Checkpoint**: At this point, User Stories 1 AND 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Detailed User Profile Inspection by Integer ID (`/users/{id}`) (Priority: P3)

**Goal**: Inspect full user profile, roles, and status by integer ID from the central directory, strictly enforcing integer routing (`/users/{id:int}`).

**Independent Test**: Call `GET /api/v1/users/1` with valid SSO token -> verify full profile is returned with `id: 1` as integer. Call `GET /api/v1/users/abc` -> verify 422 Unprocessable Entity error.

### Tests for User Story 3

- [X] T015 [P] [US3] Create unit test in `tests/unit/test_get_user_detail_use_case.py` testing `GetUserDetailUseCase` with integer ID
- [X] T016 [P] [US3] Create integration test in `tests/integration/test_external_users_api.py` testing `GET /api/v1/users/options` and `GET /api/v1/users/1` end-to-end, and verifying HTTP 422 on non-integer ID

### Implementation for User Story 3

- [X] T017 [P] [US3] Implement `GetUserDetailUseCase` in `modules/identity/use_cases/get_user_detail.py` and export in `modules/identity/use_cases/__init__.py`
- [X] T018 [US3] Register `GetUserDetailUseCase` in Dishka `IdentityProvider` in `modules/identity/di.py`
- [X] T019 [US3] Add endpoint `GET /api/v1/users/{id}` in `apps/api/routers/user_router.py` with integer path constraint (`id: int = Path(..., ge=1)`)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Architectural verification, documentation updates, and complete test suite validation

- [X] T020 Verify Clean Architecture purity gate in `tests/test_clean_architecture_purity.py` ensuring zero framework imports in `modules/identity/domain/`
- [X] T021 [P] Update documentation in `docs/ROADMAP.md` reflecting SSO-only authentication and external user directory architecture
- [X] T022 Execute quickstart validation steps from `specs/006-sso-auth-external-users/quickstart.md`
- [X] T023 Run full lint, format, and test suite verification via `uv run ruff check --fix && uv run ruff format && uv run pytest`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start immediately after Foundational (MVP!)
  - User Story 2 (P2): Depends on Foundational directory service
  - User Story 3 (P3): Depends on User Story 2 directory service & router
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- Tasks T003, T004, T005 in Phase 2 can run in parallel across different files.
- Unit tests T011, T015 can be authored in parallel.
- Documentation update T021 can run in parallel with T020.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Alembic migration)
2. Complete Phase 2: Foundational (Entities, DTOs, Interface Protocol, External Service)
3. Complete Phase 3: User Story 1 (SSO-only auth refactor)
4. **STOP and VALIDATE**: Verify SSO auth independently with `tests/integration/test_sso_only_auth.py`.
5. Deliver MVP!

### Incremental Delivery (User Stories 2, 3 & Polish)

1. Add Phase 4: User Story 2 (`/users/options` endpoint).
2. Add Phase 5: User Story 3 (`/users/{id:int}` endpoint & validation).
3. Complete Phase 6: Purity gate, documentation, and 100% test suite pass.
