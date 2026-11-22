# Tasks: Boilerplate Advanced Capabilities (DUT-AI Style)

**Input**: Design documents from `specs/002-boilerplate-extensions/` (`plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`)

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included as specified in the feature specification and architectural purity requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`, `[US4]`)
- Exact file paths included in all descriptions

---

## Phase 1: Setup (Shared Extensions Infrastructure)

**Purpose**: Initialize directory structure for pagination, frontend features, and CI workflow

- [X] T001 Create directory structure for pagination (`core/pagination/`), frontend auth feature (`web/src/features/auth/{components,hooks,services,types}`), and CI workflows (`.github/workflows/`)
- [X] T002 [P] Install frontend form dependencies (`react-hook-form`, `zod`, `@hookform/resolvers`) in `web/package.json`

---

## Phase 2: Foundational (Core Pagination Abstraction)

**Purpose**: Generic pagination and search infrastructure that user stories depend on

**⚠️ CRITICAL**: Must complete before paginated endpoints can be implemented

- [X] T003 [P] Implement `PaginationParams` (`page: int = Field(default=1, ge=1)`, `page_size: int = Field(default=20, ge=1, le=100)`, `search: str | None = None`) in `core/pagination/params.py`
- [X] T004 [P] Implement `PaginatedResponse[T]` generic model (`items: list[T]`, `total: int`, `page: int`, `page_size: int`, `total_pages: int`) in `core/pagination/response.py`
- [X] T005 Implement SQLAlchemy pagination query helper `paginate_query(session, stmt, params)` in `core/pagination/helpers.py`
- [X] T006 Expose pagination exports in `core/pagination/__init__.py`

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Full-Stack Authentication & Protected Dashboard (Priority: P1) 🎯 MVP

**Goal**: Complete end-to-end frontend authentication experience: login/register forms, Axios withCredentials + 401 interceptor, global auth context, and protected dashboard route.

**Independent Test**: Start `make dev-web`, navigate to `/dashboard` while unauthenticated to verify redirect to `/login`, submit login credentials, verify redirect to `/dashboard` with user profile displayed, and click logout to verify redirect back to `/login`.

### Implementation for User Story 1
- [X] T007 [P] [US1] Configure Axios client with `withCredentials: true` and 401 response interceptor in `web/src/lib/api.ts`
- [X] T008 [P] [US1] Define frontend auth TypeScript types (`User`, `LoginPayload`, `RegisterPayload`, `AuthContextValue`) in `web/src/features/auth/types/index.ts`
- [X] T009 [P] [US1] Implement `authService` API calls (`login`, `register`, `getMe`, `logout`) in `web/src/features/auth/services/auth-service.ts`
- [X] T010 [P] [US1] Implement TanStack Query hooks (`useUserQuery`, `useLoginMutation`, `useRegisterMutation`, `useLogoutMutation`) in `web/src/features/auth/hooks/use-auth-queries.ts`
- [X] T011 [P] [US1] Create `LoginForm` component using `react-hook-form` and `zod` validation in `web/src/features/auth/components/login-form.tsx`
- [X] T012 [P] [US1] Create `RegisterForm` component using `react-hook-form` and `zod` validation in `web/src/features/auth/components/register-form.tsx`
- [X] T013 [US1] Implement `AuthProvider` and `useAuth()` hook managing active session state in `web/src/contexts/auth-context.tsx`
- [X] T014 [US1] Wrap application root with `AuthProvider` in `web/src/app/providers.tsx` or `web/src/app/layout.tsx`
- [X] T015 [US1] Implement Login and Register pages in `web/src/app/login/page.tsx` and `web/src/app/register/page.tsx`
- [X] T016 [US1] Implement protected route layout guarding child pages with redirect to `/login` in `web/src/app/(protected)/layout.tsx`
- [X] T017 [US1] Implement user dashboard page displaying profile details and logout button in `web/src/app/(protected)/dashboard/page.tsx`

**Checkpoint**: User Story 1 is fully functional and testable in the browser.

---

## Phase 4: User Story 2 - Standardized Pagination, Filtering, and Search (Priority: P1)

**Goal**: Deliver paginated collection queries and endpoints following the standardized pagination contract.

**Independent Test**: Query `GET /api/v1/auth/users?page=1&page_size=10` and verify response structure matches `PaginatedResponse[UserResponse]`.

### Tests for User Story 2
- [X] T018 [P] [US2] Implement unit tests for `paginate_query` helper verifying offset, limit, total count, and search filtering in `tests/unit/test_pagination_helper.py`
- [X] T019 [P] [US2] Implement integration test for `GET /api/v1/auth/users` in `tests/integration/test_paginated_users.py`

### Implementation for User Story 2
- [X] T020 [P] [US2] Add `list_users(page, page_size, search)` method definition to `IUserRepository` in `modules/identity/domain/interfaces.py`
- [X] T021 [US2] Implement `list_users` in `SqlUserRepository` using `paginate_query` in `modules/identity/repository/user_repository.py`
- [X] T022 [P] [US2] Implement `ListUsersUseCase` returning `PaginatedResponse[UserResponse]` in `modules/identity/use_cases/list_users.py`
- [X] T023 [US2] Register `ListUsersUseCase` in Dishka `IdentityProvider` in `modules/identity/di.py`
- [X] T024 [US2] Implement `GET /api/v1/auth/users` endpoint with `PaginationParams` in `apps/api/routers/auth_router.py`

**Checkpoint**: User Stories 1 and 2 are functional and verified.

---

## Phase 5: User Story 3 - Background Outbox Event Dispatcher (Priority: P2)

**Goal**: Implement `OutboxProcessor` to reliably scan, execute handlers, and track failure states for background domain events.

**Independent Test**: Run `pytest tests/unit/test_outbox_processor.py` to verify handler execution and state transition to `PROCESSED` or `FAILED`.

### Tests for User Story 3
- [X] T025 [P] [US3] Implement unit tests for `OutboxProcessor` testing handler registration, successful batch processing, and exception handling in `tests/unit/test_outbox_processor.py`

### Implementation for User Story 3
- [X] T026 [P] [US3] Add `mark_failed(event_id: str, error_message: str)` method in `IOutboxRepository` and `SqlOutboxRepository` in `core/events/outbox.py`
- [X] T027 [US3] Implement `OutboxProcessor` class with handler registry and `process_pending_batch` in `core/events/processor.py`
- [X] T028 [US3] Integrate `OutboxProcessor` into ARQ worker task `process_outbox_events` in `apps/worker/main.py`

**Checkpoint**: Outbox event processor fully integrated with worker loop.

---

## Phase 6: User Story 4 - Multi-Stage Docker Builds & Automated CI/CD (Priority: P2)

**Goal**: Deliver production-ready Docker containerization and automated GitHub Actions verification.

**Independent Test**: Build Docker image via `docker build -t test-backend .` and verify non-root user execution, and run CI commands locally.

### Implementation for User Story 4
- [X] T029 [P] [US4] Implement production multi-stage `Dockerfile` with `uv` builder and non-root runner in `Dockerfile`
- [X] T030 [P] [US4] Implement multi-stage standalone `Dockerfile` for Next.js in `web/Dockerfile`
- [X] T031 [P] [US4] Implement GitHub Actions CI workflow in `.github/workflows/ci.yml` running lint, mypy, pytest, and OpenAPI drift verification

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Contract regeneration, static verification, and documentation

- [X] T032 Regenerate frontend TypeScript types via `make api-types` to include new paginated users endpoint
- [X] T033 Verify frontend type correctness via `cd web && npx tsc --noEmit`
- [X] T034 [P] Update `README.md` with instructions for pagination, frontend authentication flow, and Docker production deployment
- [X] T035 Execute full validation suite per `specs/002-boilerplate-extensions/quickstart.md` (`make test`, `make check`, `make ruff`, `make api-types`)

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Can start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1 completion - blocks User Story 2.
- **Phase 3 (User Story 1 - P1)**: Depends on Phase 1. Frontend auth flow can proceed independently.
- **Phase 4 (User Story 2 - P1)**: Depends on Phase 2 (pagination helper) and existing Identity repository.
- **Phase 5 (User Story 3 - P2)**: Depends on Phase 1. Can run in parallel with User Story 1 & 2.
- **Phase 6 (DevOps - P2)**: Can run in parallel once codebase structure is settled.
- **Phase 7 (Polish)**: Runs after all user stories are complete.
