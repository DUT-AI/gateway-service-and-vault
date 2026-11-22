# Tasks: Modular Monolith Boilerplate (DUT-AI Style)

**Input**: Design documents from `specs/001-modular-monolith-boilerplate/` (`plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`)

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included as specified in the feature specification and architectural purity requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`, `[US4]`)
- Exact file paths included in all descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project root initialization, package structure, and developer tooling

- [X] T001 Create project root folder structure (`core/`, `modules/`, `apps/api`, `apps/worker`, `apps/cli`, `migrations/`, `tests/`) per implementation plan
- [X] T002 [P] Configure root `pyproject.toml` using `uv` and `hatchling` with `packages = ["core", "modules", "apps"]` and target Python `>=3.12`
- [X] T003 [P] Configure root `.env.example` with default connection parameters for PostgreSQL, Redis, MinIO, and JWT secrets
- [X] T004 [P] Configure code formatting, linting, and type-checking rules with `ruff` and `mypy` in `pyproject.toml`
- [X] T005 [P] Setup Docker Compose configuration in `docker-compose.yml` defining services for `postgres`, `redis`, `minio`, `api`, `web`, and `worker`
- [X] T006 Implement unified root `Makefile` with commands: `dev-api`, `dev-web`, `dev-worker`, `docker-up`, `docker-down`, `migrate`, `create-migration`, `test`, `ruff`, `check`, `api-types`, `install-hooks`, and `lint`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core platform infrastructure that MUST be completed before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Implement centralized Pydantic settings in `core/config/app.py`, `core/config/database.py`, `core/config/redis.py`, `core/config/s3.py`, and `core/config/auth.py`
- [X] T008 [P] Implement core datetime helpers and ULID identifier generator in `core/utils/datetime_utils.py` and `core/utils/id_generator.py`
- [X] T009 [P] Implement standardized domain exception hierarchy (`AppException`, `DomainException`, `EntityNotFoundException`, `ConflictException`) and FastAPI global handlers in `core/exceptions/base.py` and `core/exceptions/handlers.py`
- [X] T010 [P] Implement async SQLAlchemy engine, sessionmaker, and `DatabaseProvider` in `core/database/session.py` and `core/database/base.py`
- [X] T011 [P] Implement `SqlAlchemyUnitOfWork` in `core/database/unit_of_work.py` and unit of work protocol in `core/uow.py`
- [X] T012 [P] Implement password hashing (bcrypt) and JWT encoding/decoding utilities in `core/security/password.py` and `core/security/jwt.py`
- [X] T013 [P] Implement abstract `StorageInterface` protocol and MinIO adapter in `core/storage/interface.py`, `core/storage/minio_adapter.py`, and `core/storage/di.py`
- [X] T014 Initialize root Alembic database migrations framework in `alembic.ini` and `migrations/env.py` configured to import `Base.metadata` from `core.database.base`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Developer Starts Full-Stack Application (Priority: P1) 🎯 MVP

**Goal**: Enable a developer to clone the repo, run startup commands, and have a functional FastAPI backend and Next.js frontend with active health probes.

**Independent Test**: Run `make dev-api` and verify `http://localhost:8000/health` returns status `200 OK` with database and storage health status.

### Tests for User Story 1
- [X] T015 [P] [US1] Implement integration test verifying `/health` probe returns 200 with component statuses in `tests/integration/test_health.py`

### Implementation for User Story 1
- [X] T016 [P] [US1] Implement health check functions for database, redis, and minio connections in `apps/api/health.py`
- [X] T017 [P] [US1] Create health router exposing `GET /health` in `apps/api/routers/health_router.py`
- [X] T018 [US1] Create FastAPI application instance with `AppCORSMiddleware`, OpenTelemetry tracing hook, and global exception handlers in `apps/api/main.py`
- [X] T019 [US1] Verify local service startup via `make dev-api` and confirm `/health` and OpenAPI docs `/docs` render properly

**Checkpoint**: User Story 1 is functional and verifiable independently.

---

## Phase 4: User Story 2 - Developer Implements a New Feature Module Following Clean Architecture (Priority: P1)

**Goal**: Deliver a complete reference feature module (`modules/identity`) strictly adhering to Clean Architecture with zero framework imports in domain, Dishka DI, and user authentication.

**Independent Test**: Run `pytest tests/test_clean_architecture_purity.py` to confirm zero framework imports in domain, and test `/api/v1/auth/register`, `/login`, and `/me` end-to-end.

### Tests for User Story 2
- [X] T020 [P] [US2] Implement architectural purity gate test verifying domain entities do not import `pydantic`, `fastapi`, or `sqlalchemy` in `tests/test_clean_architecture_purity.py`
- [X] T021 [P] [US2] Implement unit tests for identity use cases using in-memory mock repositories in `tests/unit/test_identity_use_cases.py`
- [X] T022 [P] [US2] Implement integration test for authentication API endpoints in `tests/integration/test_auth_api.py`

### Implementation for User Story 2
- [X] T023 [P] [US2] Create pure domain entity `UserEntity` (with verbatim fields: `id: int`, `email: str`, `name: str | None = None`, `role: str = "user"`, `password_hash: str | None = None`, `avatar_url: str | None = None`, `status: str = "ACTIVE"`, `created_at: datetime | None = None`) and `AuthPayload` in `modules/identity/domain/entities.py`
- [X] T024 [P] [US2] Define domain repository interface `IUserRepository` and domain exceptions in `modules/identity/domain/interfaces.py` and `modules/identity/domain/exceptions.py`
- [X] T025 [P] [US2] Create Pydantic DTOs `UserRegisterRequest` (`email: EmailStr`, `password: str = Field(..., min_length=8, max_length=128)`, `name: str | None = Field(None, max_length=255)`), `UserLoginRequest`, `TokenResponse`, and `UserResponse` in `modules/identity/dtos/auth_dtos.py`
- [X] T026 [P] [US2] Create SQLAlchemy ORM model `UserModel` mapped to `users` with verbatim columns (`id: int primary_key`, `email: String(255) unique index`, `role: String(50)`, `status: String(50)`) in `modules/identity/models/user.py`
- [X] T027 [US2] Implement concrete repository `SqlUserRepository` implementing `IUserRepository` using `AsyncSession` in `modules/identity/repository/user_repository.py`
- [X] T028 [P] [US2] Implement `RegisterUserUseCase` validating email uniqueness, hashing password with bcrypt, and persisting via repository in `modules/identity/use_cases/register_user.py`
- [X] T029 [P] [US2] Implement `LoginUserUseCase` verifying credentials and issuing JWT bearer token in `modules/identity/use_cases/login_user.py`
- [X] T030 [P] [US2] Implement `GetCurrentUserUseCase` extracting authenticated user from `AuthPayload` in `modules/identity/use_cases/get_current_user.py`
- [X] T031 [US2] Implement Dishka `IdentityProvider` registering repository and use cases with `Scope.REQUEST` in `modules/identity/di.py`
- [X] T032 [US2] Assemble global Dishka DI container binding `DatabaseProvider`, `StorageProvider`, and `IdentityProvider` in `apps/api/di.py`
- [X] T033 [US2] Implement auth router endpoints (`POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`) injecting use cases via `FromDishka` in `apps/api/routers/auth_router.py`
- [X] T034 [US2] Register `auth_router` in `apps/api/main.py` and setup Dishka with FastAPI app
- [X] T035 [US2] Create initial Alembic database migration script for `users` table in `migrations/versions/001_create_users_table.py`

**Checkpoint**: User Story 1 and 2 are fully functional and pass architectural purity gates.

---

## Phase 5: User Story 3 - Full-Stack Type Synchronization (Priority: P2)

**Goal**: Enable frontend developers to automatically synchronize backend DTOs to TypeScript type definitions without running a web server.

**Independent Test**: Run `make api-types` from root and verify `web/src/types/api.generated.d.ts` is updated and `cd web && pnpm typecheck` passes.

### Implementation for User Story 3
- [X] T036 [P] [US3] Implement offline OpenAPI schema exporter script in `apps/api/openapi_export.py` writing schema to `web/openapi.json`
- [X] T037 [US3] Update `web/package.json` with scripts `"sync:api": "uv run --directory .. python -m apps.api.openapi_export web/openapi.json && pnpm generate:api"` and `"generate:api": "openapi-typescript ./openapi.json -o src/types/api.generated.d.ts"`
- [X] T038 [US3] Configure `api-types` target in root `Makefile` triggering frontend sync script
- [X] T039 [US3] Run `make api-types` and verify generated TypeScript definitions in `web/src/types/api.generated.d.ts`

**Checkpoint**: Type synchronization from backend to frontend works offline.

---

## Phase 6: User Story 4 - Asynchronous Background Tasks & Event Processing (Priority: P3)

**Goal**: Provide an asynchronous task queue engine using Redis + ARQ and an outbox event persistence pattern for background processing.

**Independent Test**: Trigger an ARQ background task and verify worker executes the task function and logs success.

### Tests for User Story 4
- [X] T040 [P] [US4] Implement unit test for ARQ task functions and outbox publishing in `tests/unit/test_worker_tasks.py`

### Implementation for User Story 4
- [X] T041 [P] [US4] Define `OutboxEventModel` mapped to table `outbox_events` with fields (`id: String(36)`, `event_type: String(100)`, `payload: JSON`, `status: String(50)`) in `core/events/models.py`
- [X] T042 [P] [US4] Implement Outbox repository and domain event processor in `core/events/outbox.py` and `core/events/domain_event.py`
- [X] T043 [P] [US4] Implement ARQ worker entry point with `WorkerSettings` and task functions `send_welcome_email` and `process_outbox_events` in `apps/worker/main.py`
- [X] T044 [US4] Create Alembic migration for `outbox_events` table in `migrations/versions/002_create_outbox_table.py`
- [X] T045 [US4] Configure `dev-worker` target in `Makefile` to launch ARQ worker via `uv run arq apps.worker.main.WorkerSettings`

**Checkpoint**: Background task worker and outbox pattern operational.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, documentation, git pre-commit hooks, and complete end-to-end verification

- [X] T046 [P] Implement git pre-commit hook script in `.githooks/pre-commit` verifying `ruff format`, `ruff check`, `mypy`, and `pytest`
- [X] T047 [P] Create CLI management utility in `apps/cli/manage.py` for database inspection and admin seeding
- [X] T048 Remove obsolete nested `backend/` directory once root modular structure is verified
- [X] T049 [P] Update root `README.md` with complete architecture guide, project layout, and developer commands
- [X] T050 Execute full validation suite per `specs/001-modular-monolith-boilerplate/quickstart.md` (`make test`, `make check`, `make ruff`, `make api-types`)

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Can start immediately - no dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 completion - **BLOCKS all user stories**.
- **Phase 3 (User Story 1 - P1)**: Depends on Phase 2. Enables MVP deployment.
- **Phase 4 (User Story 2 - P1)**: Depends on Phase 2. Can run in parallel with or immediately after Phase 3.
- **Phase 5 (User Story 3 - P2)**: Depends on Phase 4 (requires auth DTOs and routes to export OpenAPI).
- **Phase 6 (User Story 4 - P3)**: Depends on Phase 2 and Redis setup.
- **Phase 7 (Polish)**: Depends on completion of all desired user stories.

### Parallel Opportunities

- **Phase 1**: T002, T003, T004, T005 can all execute in parallel.
- **Phase 2**: T008, T009, T010, T011, T012, T013 can execute in parallel once T007 settings are ready.
- **Phase 4 (US2)**:
  - T020 (Purity test), T021 (Domain entities), T024 (Repository interface), T025 (Pydantic DTOs), T026 (SQLAlchemy model) can all be authored in parallel.
  - Once entities/repos/DTOs are in place, T028, T029, T030 (Use cases) can be written in parallel.

---

## Parallel Example: User Story 2 (Clean Architecture Module)

```bash
# Launch parallel creation of domain, DTOs, and persistence models:
Task: "T023 [P] [US2] Create pure domain entity UserEntity in modules/identity/domain/entities.py"
Task: "T025 [P] [US2] Create Pydantic DTOs in modules/identity/dtos/auth_dtos.py"
Task: "T026 [P] [US2] Create SQLAlchemy ORM model UserModel in modules/identity/models/user.py"

# Launch parallel creation of use cases once models & interfaces are ready:
Task: "T028 [P] [US2] Implement RegisterUserUseCase in modules/identity/use_cases/register_user.py"
Task: "T029 [P] [US2] Implement LoginUserUseCase in modules/identity/use_cases/login_user.py"
Task: "T030 [P] [US2] Implement GetCurrentUserUseCase in modules/identity/use_cases/get_current_user.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + Core Foundation)
1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Complete Phase 3 (User Story 1 - Full-stack launch + health check).
3. **VALIDATE MVP**: Confirm `make dev-api` starts and `/health` returns 200.

### Incremental Feature Delivery
1. Implement Phase 4 (User Story 2 - Clean Architecture Identity module). Validate with `tests/test_clean_architecture_purity.py`.
2. Implement Phase 5 (User Story 3 - Offline API type sync). Validate with `make api-types`.
3. Implement Phase 6 (User Story 4 - Redis + ARQ background worker).
4. Run Phase 7 (Polish & cleanup).
