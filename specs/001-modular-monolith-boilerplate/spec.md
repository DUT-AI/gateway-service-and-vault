# Feature Specification: Modular Monolith Boilerplate (DUT-AI Style)

**Feature Branch**: `001-modular-monolith-boilerplate`

**Created**: 2026-11-22

**Status**: Draft

**Input**: User description: "Tôi muốn copy style code của dự án dut-ai-data-platform sang để tạo ra 1 project-boilderplate, hãy nghiên cứu tìm hiểu cho tôi"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Starts Full-Stack Application (Priority: P1)

As a software engineer starting a new project, I want to clone the boilerplate and launch the entire local development environment (API, Web, Database, Cache, and Services) with a single command so that I can immediately begin writing business features without configuring infrastructure from scratch.

**Why this priority**: Core value of a project boilerplate. It provides immediate developer onboarding and a functional baseline.

**Independent Test**: Can be tested by running `make docker-up` or local dev commands (`make dev-api` and `make dev-web`) and confirming both backend API (Swagger UI at `/docs`) and frontend Next.js application load without errors.

**Acceptance Scenarios**:

1. **Given** a clean development environment with Docker and `uv` installed, **When** the developer runs the startup command, **Then** all backing services (PostgreSQL, Redis, Storage) and application services start up healthy.
2. **Given** the backend API is running, **When** the developer requests the health check endpoint `/health`, **Then** the service returns status 200 with operational status for database and storage components.

---

### User Story 2 - Developer Implements a New Feature Module Following Clean Architecture (Priority: P1)

As a backend engineer, I want a standard modular architecture where each feature lives in its own decoupled module (`modules/<feature_name>`) with pure domain logic, separate DTOs, SQLAlchemy persistence models, and Dishka dependency injection, so that business logic remains clean, testable, and maintainable.

**Why this priority**: Guarantees architectural consistency across team members and enforces DDD boundary separation.

**Independent Test**: Can be tested by creating or inspecting a reference module, executing the architectural purity test suite, and verifying zero forbidden framework imports (`pydantic`, `fastapi`, `sqlalchemy`) in the domain layer.

**Acceptance Scenarios**:

1. **Given** an existing or newly generated domain entity in `modules/<feature_name>/domain/entities.py`, **When** the developer runs `make test` or `pytest tests/test_clean_architecture_purity.py`, **Then** the purity gate verifies zero dependencies on web/ORM frameworks and passes.
2. **Given** a new use case requiring database access, **When** the use case executes within an API request, **Then** Dishka injects the session and repository automatically without manual session lifecycle management in the router.

---

### User Story 3 - Full-Stack Type Synchronization (Priority: P2)

As a frontend developer, I want to automatically regenerate TypeScript types and API client interfaces from backend Python DTOs without needing a running server instance, so that frontend components stay type-safe and synchronized with API contract changes.

**Why this priority**: Eliminates manual type copying, avoids runtime type mismatches between frontend and backend, and speeds up feature development.

**Independent Test**: Can be tested by running `make api-types` (or `pnpm sync:api`) from the project root and confirming updated TypeScript types appear in `web/src/types/api.generated.d.ts`.

**Acceptance Scenarios**:

1. **Given** a new backend endpoint and response DTO, **When** the developer executes `make api-types`, **Then** an OpenAPI schema is generated offline and converted to TypeScript definition files under the web workspace.
2. **Given** a breaking field name change in a backend DTO, **When** `make api-types` and `pnpm typecheck` are executed, **Then** the frontend build tool flags affected client components at compile time.

---

### User Story 4 - Asynchronous Background Tasks & Event Processing (Priority: P3)

As a developer building asynchronous workflows, I want an outbox pattern and background worker runner pre-configured in the boilerplate, so that heavy computations and asynchronous notifications can be processed reliably outside HTTP request cycles.

**Why this priority**: Enables enterprise workloads (file imports, AI model inference, async notifications) without having to architect queuing mechanisms later.

**Independent Test**: Can be tested by submitting a background job payload or publishing a domain event to the outbox and confirming the worker processes the event and persists state transitions.

**Acceptance Scenarios**:

1. **Given** an asynchronous job trigger, **When** a use case emits a background task, **Then** the worker process claims the job and executes it without blocking the HTTP response.

---

### Edge Cases

- **Illegal Framework Import in Domain**: A developer accidentally imports `pydantic` or `sqlalchemy` in `domain/entities.py`. The architectural purity test suite must detect this during `make test` and `make check`, failing the build with a descriptive error.
- **Cross-Module Direct Data Access**: A module attempts to directly query another module's database tables or internal repositories. The boilerplate documentation and client pattern (`modules/<name>/client`) must prescribe inter-module communication boundaries.
- **Offline API Generation Failure**: If backend code has a syntax or import error, the `make api-types` script must fail fast with meaningful stack traces instead of silently emitting an empty OpenAPI specification.
- **Database Migration Divergence**: When multiple modules introduce schema changes, Alembic migrations must maintain a clean linear revision sequence across all modular models.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST organize project root into a Modular Monolith structure featuring:
  - `core/`: Shared infrastructure (database engine/session, config, security, storage adapter, exception handling, outbox, telemetry).
  - `modules/`: Decoupled business domains with strict Clean Architecture layers (`domain/`, `dtos/`, `models/`, `repository/`, `use_cases/`, `client/`, `di.py`).
  - `apps/`: Deployable targets including `apps/api` (FastAPI), `apps/worker` (background tasks), and `apps/cli` (command line utilities).
  - `migrations/`: Unified Alembic migrations at the root level.
  - `tests/`: Automated testing including architectural purity tests, unit tests, and integration tests.
  - `web/`: Next.js frontend application with TypeScript, Tailwind CSS, and TanStack Query.
- **FR-002**: Domain layer in every module MUST be 100% pure Python entities and value objects with ZERO imports from frameworks (`pydantic`, `fastapi`, `sqlalchemy`).
- **FR-003**: System MUST provide an automated architectural purity test (`tests/test_clean_architecture_purity.py`) that introspects all domain packages and fails if framework imports are detected.
- **FR-004**: Dependency injection MUST be managed via Dishka, providing scoped dependencies (`Scope.REQUEST`, `Scope.APP`) for database sessions, repositories, use cases, and external adapters.
- **FR-005**: Core infrastructure MUST provide centralized exception handling with custom domain exceptions (`AppException`, `DomainException`, `EntityNotFoundException`, `ConflictException`) mapped to standardized JSON responses in FastAPI.
- **FR-006**: Storage layer in `core/storage` MUST expose an abstraction protocol (`StorageInterface`) with a production-ready S3/MinIO adapter for binary asset management.
- **FR-007**: System MUST provide an automated offline API type synchronization command (`make api-types`) that exports the FastAPI OpenAPI specification and generates TypeScript types for the frontend.
- **FR-008**: System MUST include a production-ready Identity & Authentication reference module (`modules/identity`) implementing the complete Clean Architecture flow with User domain entity, JWT token issuance and verification, password hashing with bcrypt, Pydantic DTOs, SQLAlchemy persistence models, Dishka DI provider, and FastAPI authentication endpoints (Login, Register, and Get Current User).
- **FR-009**: System MUST provide a lightweight asynchronous worker and task queue engine powered by Redis and ARQ, including task definitions, worker entry point in `apps/worker`, and health/connectivity checks.
- **FR-010**: System MUST provide a unified root `Makefile` and pre-commit githooks enforcing `ruff` formatting/linting, `mypy` strict type checking, and test execution.

### Key Entities *(include if feature involves data)*

- **Domain Entity**: Plain Python dataclass defining core business attributes and domain invariants without ORM annotations.
- **ORM Persistence Model**: SQLAlchemy declarative base model mapping relational tables in the database.
- **DTO (Data Transfer Object)**: Pydantic schema used for API contract serialization, validation, and documentation.
- **Use Case**: Application service encapsulating a single business workflow and executing within transaction boundaries.
- **Dishka Provider**: Dependency injection configuration binding interfaces to concrete implementations and managing lifecycles.
- **Outbox Message**: Persistent record of domain events to be reliably delivered by the background processor.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new developer can set up and run the full stack (API, Web, DB, Storage) in under 3 minutes using standard project commands.
- **SC-002**: Architectural purity gate executes in under 5 seconds and catches 100% of illegal framework dependencies in the domain layer.
- **SC-003**: Backend contract changes can be synchronized to frontend TypeScript types in under 10 seconds without needing to start the backend HTTP server.
- **SC-004**: 100% of codebase passes code quality gates (`ruff` format, `ruff` lint, `mypy` strict checks) with zero errors out-of-the-box.
- **SC-005**: All baseline unit and integration tests achieve 100% pass rate in standard local and containerized environments.

## Assumptions

- Developers have Python 3.12+, `uv` (Fast Python package manager), Node.js (with `pnpm`), and Docker Compose installed.
- The backend relies on PostgreSQL as the primary relational database and asyncpg as the asynchronous DB driver.
- The frontend uses Next.js (App Router) with React 19, Tailwind CSS, and TanStack Query.
- S3-compatible object storage (e.g., MinIO for local dev, AWS S3 for production) is used for file/binary asset uploads.
