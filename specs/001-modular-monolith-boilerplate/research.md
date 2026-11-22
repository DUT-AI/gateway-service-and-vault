# Phase 0 Research & Technical Decisions: Modular Monolith Boilerplate (DUT-AI Style)

## Overview
This document consolidates research and design decisions made to replicate the robust, scalable architecture and code style of `dut-ai-data-platform` into `project-boilerplate`.

---

## Decision 1: Root-Level Modular Monolith Architecture

### Decision
Structure the repository as a unified root workspace containing `core/`, `modules/`, `apps/`, `migrations/`, `tests/`, and `web/`, configured via a root `pyproject.toml` (using `uv` + `hatchling`) with `packages = ["core", "modules", "apps"]`.

### Rationale
- **Direct Alignment with `dut-ai-data-platform`**: In `dut-ai-data-platform`, backend code is not buried inside a `backend/app/` subdirectory. Root packaging allows clean absolute imports (`core.database.session`, `modules.identity.domain.entities`, `apps.api.main`).
- **Unified Tooling**: Running `uv run pytest`, `uv run ruff check`, and `uv run mypy core modules apps` operates seamlessly from the workspace root without requiring directory switching.
- **Contract Exporting**: Enables the frontend script (`make api-types`) to run `uv run python -m apps.api.openapi_export` directly and feed the output into `openapi-typescript` within the `web/` workspace.

### Alternatives Considered
- **Nested `backend/` directory (current state)**:
  - *Drawbacks*: Forces dual configuration files, awkward relative paths in `Makefile` (`cd ./backend && uv run...`), broken root import paths, and disconnects the API schema generator from the frontend.

---

## Decision 2: Clean Architecture & Domain Purity Invariant

### Decision
Enforce strict Clean Architecture layers within every module under `modules/<feature_name>/`:
1. `domain/`: Pure domain entities (`@dataclass`), value objects, domain interfaces, and domain exceptions. **ZERO framework imports** (`pydantic`, `fastapi`, `sqlalchemy`).
2. `dtos/`: Pydantic models for request/response serialization and validation.
3. `models/`: SQLAlchemy ORM declarative models.
4. `repository/`: Concrete repository implementations adhering to domain interfaces.
5. `use_cases/`: Business logic orchestration.
6. `client/`: Internal inter-module communication client and interfaces.
7. `di.py`: Dishka dependency injection provider.

This is strictly protected by `tests/test_clean_architecture_purity.py`.

### Rationale
- Decouples core business rules from fast-changing libraries or frameworks.
- Makes unit tests blazing fast without needing database engines or HTTP mocks.
- Prevents ORM leaky abstractions (e.g. lazy loading issues or database coupling in business decisions).

### Alternatives Considered
- **Pydantic Models as Domain Entities**:
  - *Drawbacks*: Conflates API input parsing/validation with domain invariants; introduces runtime overhead and couples domain logic to serialization frameworks.
- **Active Record / Fat SQLAlchemy Models**:
  - *Drawbacks*: Couples persistence directly to business objects, making unit testing slow and domain logic difficult to evolve.

---

## Decision 3: Dependency Injection Framework (Dishka)

### Decision
Use **Dishka** as the exclusive IoC/DI container for the entire platform:
- Every module defines a `Provider` in `modules/<name>/di.py` specifying `Scope.APP` (singletons, HTTP clients, engines) and `Scope.REQUEST` (sessions, repositories, use cases).
- `core/` defines `DatabaseProvider` and `StorageProvider`.
- `apps/api/di.py` bundles all providers using `make_async_container(...)` and mounts it to FastAPI via `setup_dishka(container, app)`.
- Routers inject use cases using `FromDishka[UseCaseClass]`.

### Rationale
- Native `async`/`await` support with deterministic scoping and automated async context manager cleanup (`try ... yield session ... commit/rollback`).
- Unlike FastAPI's default `Depends()`, Dishka providers are completely decoupled from HTTP requests, allowing the exact same providers to be reused in CLI scripts (`apps/cli`), background workers (`apps/worker`), and integration test suites (`tests/conftest.py`).

### Alternatives Considered
- **FastAPI `Depends()` only**:
  - *Drawbacks*: Strongly coupled to HTTP request cycles; cannot be cleanly injected into standalone CLI tools or ARQ background workers without re-inventing DI.
- **Python `dependency-injector`**:
  - *Drawbacks*: Heavier syntax, less ergonomic async lifecycle support compared to Dishka.

---

## Decision 4: Asynchronous Worker & Queuing Engine (Redis + ARQ)

### Decision
Integrate **Redis** with **ARQ** (`arq>=0.26.0`) for asynchronous background processing located in `apps/worker/`:
- `apps/worker/main.py`: Defines the ARQ `WorkerSettings`, redis pool configuration, on_startup/on_shutdown hooks, and task functions.
- `core/config/redis.py`: Centralized Pydantic settings for Redis connection URL and pool limits.
- Tasks are invoked from use cases or API routers via an injected ARQ Redis client.

### Rationale
- User explicitly selected lightweight Redis/ARQ over full RabbitMQ.
- Async-native (built on top of `asyncio` and `redis-py`).
- Extremely lightweight footprint compared to RabbitMQ + Celery; requires only a standard Redis container, which is already useful for caching.

### Alternatives Considered
- **RabbitMQ + aio-pika / Celery** (as in full `dut-ai-data-platform`):
  - *Drawbacks*: Overkill for a general-purpose project boilerplate; requires running a heavy Erlang-based message broker container.
- **FastAPI `BackgroundTasks`**:
  - *Drawbacks*: Runs inside the same uvicorn process; if the web server restarts or crashes, tasks are dropped without retry mechanisms.

---

## Decision 5: Offline API Contract Synchronization (`sync:api`)

### Decision
Implement an offline OpenAPI exporter (`apps/api/openapi_export.py`) combined with `openapi-typescript` in the frontend:
1. `apps/api/openapi_export.py`: Instantiates the FastAPI application, extracts `app.openapi()`, and writes `web/openapi.json`.
2. `web/package.json`: Script `"sync:api": "uv run --directory .. python -m apps.api.openapi_export web/openapi.json && pnpm generate:api"`.
3. `openapi-typescript` generates `web/src/types/api.generated.d.ts`.

### Rationale
- Completely eliminates drift between Python DTOs and TypeScript interfaces.
- Runs statically in CI or local pre-commit without starting a web server or connecting to a live database.
- Guarantees immediate TypeScript compilation errors when backend API contracts change incompatibly.

### Alternatives Considered
- **Running a dev server and fetching `http://localhost:8000/openapi.json`**:
  - *Drawbacks*: Flaky; requires developers to spin up backend services and database migrations just to update frontend types.
