# Implementation Plan: Modular Monolith Boilerplate (DUT-AI Style)

**Branch**: `001-modular-monolith-boilerplate` | **Date**: 2026-11-22 | **Spec**: [spec.md](file:///Users/nguyenhuynh/Documents/projects/project-boilerplate/specs/001-modular-monolith-boilerplate/spec.md)

**Input**: Feature specification from `specs/001-modular-monolith-boilerplate/spec.md`

## Summary

Restructure `project-boilerplate` to faithfully adopt the architecture, code styles, and engineering practices of `dut-ai-data-platform`:
1. Elevate backend from nested `backend/` to root-level Modular Monolith (`core/`, `modules/`, `apps/`, `migrations/`, `tests/`).
2. Implement shared infrastructure in `core/` (database session pool, Pydantic settings config, security/JWT, custom exceptions & handlers, MinIO/S3 storage adapter, Outbox pattern).
3. Implement `modules/identity` as the reference module adhering strictly to Clean Architecture (Pure domain entities with zero framework dependencies, Pydantic DTOs, SQLAlchemy ORM models, repository implementation, use cases, Dishka DI Provider).
4. Implement `apps/api` (FastAPI with Dishka container and OpenAPI export), `apps/worker` (Redis + ARQ), and `apps/cli`.
5. Implement the Architectural Purity Gate (`tests/test_clean_architecture_purity.py`) and full test coverage.
6. Connect offline OpenAPI schema export to frontend TypeScript generation (`make api-types`).
7. Unify project root `Makefile`, `docker-compose.yml`, and `.githooks/pre-commit`.

---

## Technical Context

**Language/Version**: Python 3.12 (managed via `uv`), TypeScript 5.x (Node.js 20+, managed via `pnpm 9+`).

**Primary Dependencies**:
- **Backend API & DI**: FastAPI (`>=0.115.0`), Dishka (`>=1.4.0`), Pydantic v2 (`>=2.9.0`), Pydantic-Settings (`>=2.4.0`), Uvicorn.
- **Persistence & Storage**: SQLAlchemy 2.0 (`>=2.0.0`), Asyncpg (`>=0.29.0`), Greenlet, Alembic (`>=1.13.0`), Boto3 (MinIO/S3).
- **Background Tasks & Queue**: Redis (`>=5.0.0`), ARQ (`>=0.26.0`).
- **Security & Utilities**: PyJWT (`>=2.9.0`), Bcrypt (`>=4.2.0`), Loguru, Python-ULID.
- **Frontend**: Next.js 16 (App Router), React 19, Tailwind CSS v4, TanStack React Query, Radix UI, OpenAPI-TypeScript.

**Storage**: PostgreSQL 16 (Relational DB), Redis 7 (Cache & Task Queue), MinIO (S3 Object Storage).

**Testing**: Pytest (`pytest-asyncio`, `pytest-cov`, `aiosqlite`), custom Architectural Purity Gate test suite.

**Target Platform**: Linux / macOS development environment, Docker & Docker Compose containerized deployment.

**Project Type**: Full-stack web application & enterprise modular boilerplate.

**Performance Goals**: API response times < 50ms p95 for core auth queries, purity tests execute in < 5 seconds.

**Constraints**: Domain entities MUST have zero dependencies on frameworks (`pydantic`, `fastapi`, `sqlalchemy`). Offline contract generation must not require a live database or running web server.

---

## Constitution Check

*GATE: Checked against Spec-Kit project principles and Clean Architecture rules.*

| Principle / Rule | Compliance Status | Analysis |
|------------------|-------------------|----------|
| **Domain Purity** | **PASS** | Domain entities in `modules/identity/domain/entities.py` use pure `@dataclass`, zero framework imports. Guarded by automated test. |
| **Separation of Concerns** | **PASS** | `core/` contains generic infrastructure; `modules/` contains business domain; `apps/` contains runnable targets. |
| **Dependency Inversion** | **PASS** | Business logic (use cases) depends on domain interfaces (`IUserRepository`); Dishka injects concrete implementations. |
| **Single Source of Truth Contracts** | **PASS** | Backend DTOs determine OpenAPI schemas, which generate frontend TypeScript types via `make api-types`. |
| **Reproducibility** | **PASS** | Root `uv.lock` and `pnpm-lock.yaml` lock all dependency versions; `docker-compose.yml` orchestrates dependencies. |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-modular-monolith-boilerplate/
├── plan.md              # Implementation Plan (this file)
├── research.md          # Technical decisions and architecture comparisons
├── data-model.md        # Domain entities, ORM models, DTOs, Outbox schemas
├── quickstart.md        # Run and validation guide
├── contracts/           # API contracts, Worker task signatures, Storage interface
│   ├── identity-api.json
│   ├── worker-contract.md
│   └── storage-interface.md
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root layout)

```text
project-boilerplate/
├── core/                        # Shared platform infrastructure
│   ├── database/
│   │   ├── base.py              # DeclarativeBase for SQLAlchemy
│   │   ├── session.py           # AsyncEngine, AsyncSessionLocal, DatabaseProvider
│   │   └── unit_of_work.py      # SqlAlchemyUnitOfWork implementation
│   ├── config/                  # Pydantic Settings
│   │   ├── app.py
│   │   ├── database.py
│   │   ├── redis.py
│   │   ├── s3.py
│   │   └── auth.py
│   ├── security/                # JWT, bcrypt password hashing, auth dependencies
│   │   ├── jwt.py
│   │   ├── password.py
│   │   └── deps.py
│   ├── exceptions/              # Standardized exception hierarchy & FastAPI handlers
│   │   ├── base.py
│   │   └── handlers.py
│   ├── storage/                 # Storage abstraction & MinIO adapter
│   │   ├── interface.py
│   │   ├── minio_adapter.py
│   │   └── di.py
│   ├── events/                  # Outbox pattern & domain event definitions
│   │   ├── domain_event.py
│   │   ├── outbox.py
│   │   └── models.py
│   └── utils/                   # ULID id_generator, datetime_utils
│       ├── id_generator.py
│       └── datetime_utils.py
│
├── modules/                     # Business domain modules
│   └── identity/                # Reference Auth & User module
│       ├── domain/              # Pure domain entities, interfaces, exceptions
│       │   ├── entities.py
│       │   ├── interfaces.py
│       │   └── exceptions.py
│       ├── dtos/                # Pydantic request/response schemas
│       │   └── auth_dtos.py
│       ├── models/              # SQLAlchemy mapped models
│       │   └── user.py
│       ├── repository/          # Concrete SQLAlchemy repositories
│       │   └── user_repository.py
│       ├── use_cases/           # Application use cases
│       │   ├── register_user.py
│       │   ├── login_user.py
│       │   └── get_current_user.py
│       └── di.py                # Identity Dishka DI Provider
│
├── apps/                        # Deployable applications
│   ├── api/                     # FastAPI entry point
│   │   ├── main.py              # App setup, CORS, Telemetry, Routers, Dishka
│   │   ├── di.py                # Global Dishka container bootstrap
│   │   ├── openapi_export.py    # Offline OpenAPI JSON exporter
│   │   └── routers/             # API router endpoints
│   │       ├── auth_router.py
│   │       └── health_router.py
│   ├── worker/                  # Background worker (Redis + ARQ)
│   │   └── main.py
│   └── cli/                     # CLI management scripts
│       └── manage.py
│
├── migrations/                  # Alembic migrations (root-level)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── tests/                       # Automated test suite
│   ├── conftest.py              # Fixtures & in-memory test DB / Dishka test container
│   ├── test_clean_architecture_purity.py
│   ├── unit/                    # Unit tests for domain & use cases
│   └── integration/             # API endpoint & database tests
│
├── web/                         # Next.js frontend workspace
│   ├── package.json
│   ├── src/
│   │   ├── app/
│   │   ├── features/
│   │   └── types/
│   │       └── api.generated.d.ts # Synchronized via make api-types
│
├── .githooks/
│   └── pre-commit               # Git pre-commit verification script
├── docker-compose.yml           # PostgreSQL, Redis, MinIO, API, Web, Worker
├── Makefile                     # Unified development commands
└── pyproject.toml               # Root uv workspace package
```

**Structure Decision**: Fully adopt the root-level layout of `dut-ai-data-platform` where `core/`, `modules/`, and `apps/` are packaged directly at root, deprecating the single nested `backend/` directory.

---

## Complexity Tracking

| Component | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| **Dishka DI Container** | Decouples use cases and repositories from web frameworks, enabling re-use in CLI and workers. | FastAPI `Depends` couples logic to HTTP request scope only. |
| **Architectural Purity Test** | Guarantees that team members do not pollute pure business domain with ORM/HTTP frameworks over time. | Manual code review alone frequently misses leaky framework imports. |
| **Offline OpenAPI Export** | Allows frontend developers to update types without needing local DB setup or running containers. | Live server crawling requires running servers and active network ports. |
| **Modular Monolith Layout** | Provides clear boundaries between business domains while keeping deployment simple in a single repository. | Microservices create excessive DevOps overhead; spaghetti single app lacks domain boundaries. |
