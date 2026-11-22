# Project Boilerplate

A production-ready Modular Monolith backend and web interface with Clean Architecture, Domain-Driven Design (DDD), Dishka Dependency Injection, FastAPI, and Next.js. Engineered following the proven patterns of `dut-ai-data-platform`.

## Architecture Overview

```text
project-boilerplate/
├── core/                        # Shared platform infrastructure
│   ├── database/                # AsyncEngine, AsyncSessionLocal, DatabaseProvider, UoW
│   ├── config/                  # Pydantic Settings (app, database, redis, s3, auth)
│   ├── security/                # JWT, bcrypt, auth dependencies
│   ├── exceptions/              # Standardized exception hierarchy & FastAPI handlers
│   ├── storage/                 # StorageInterface & MinIO/S3 adapter
│   ├── events/                  # Outbox pattern & domain events
│   └── utils/                   # ULID id_generator, datetime_utils
│
├── modules/                     # Decoupled business domain modules
│   └── identity/                # Reference Clean Architecture module
│       ├── domain/              # Pure entities (@dataclass, ZERO framework imports)
│       ├── dtos/                # Pydantic request/response schemas
│       ├── models/              # SQLAlchemy mapped models
│       ├── repository/          # Concrete SQLAlchemy repositories
│       ├── use_cases/           # Application use cases (Register, Login, GetMe)
│       └── di.py                # Identity Dishka DI Provider
│
├── apps/                        # Deployable applications
│   ├── api/                     # FastAPI entrypoint, routers, Dishka container, openapi_export
│   ├── worker/                  # Background task worker (Redis + ARQ)
│   └── cli/                     # Management & seed scripts
│
├── migrations/                  # Alembic migrations at root
├── tests/                       # Test suite with architectural purity gate tests
├── web/                         # Next.js 16 frontend (App Router, Tailwind v4, TanStack Query)
├── docker-compose.yml           # PostgreSQL, Redis, MinIO, API, Web, Worker
├── Makefile                     # Unified developer commands
└── pyproject.toml               # Root uv workspace package
```

## Key Architectural Principles

1. **Modular Monolith**: Modules in `modules/<name>` represent bounded business contexts, each containing its own Domain, DTOs, Persistence Models, Repositories, Use Cases, and DI Provider.
2. **Clean Architecture Purity Invariant**: Domain entities in `modules/*/domain/entities.py` are pure Python dataclasses with **ZERO framework imports** (`pydantic`, `fastapi`, `sqlalchemy`). This invariant is strictly enforced by `tests/test_clean_architecture_purity.py`.
3. **IoC & Dependency Injection with Dishka**: Every module exposes a `Provider`. Dishka cleanly manages async lifecycle scoping (`Scope.APP`, `Scope.REQUEST`) and transactions without coupling logic to HTTP controllers.
4. **Offline Type Synchronization**: Changes to backend DTOs can be exported to frontend TypeScript definitions statically via `make api-types` without starting a web server.
5. **Asynchronous Background Processing**: Lightweight Redis + ARQ task runner for executing background jobs and dispatching outbox events.

## Quickstart

### 1. Prerequisites
- Python `>= 3.12` and [`uv`](https://github.com/astral-sh/uv)
- Node.js `>= 20` and `pnpm` / `npm`
- Docker & Docker Compose

### 2. Setup & Installation
```bash
# Clone and configure environment
cp .env.example .env

# Install pre-commit hooks
make install-hooks

# Start backing services (PostgreSQL, Redis, MinIO)
make docker-up

# Install Python packages & run database migrations
uv sync
make migrate
```

### 3. Development Commands

| Command | Description |
|---|---|
| `make dev-api` | Start local FastAPI dev server with auto-reload at `http://localhost:8000` |
| `make dev-web` | Start Next.js frontend dev server at `http://localhost:3000` |
| `make dev-worker` | Start ARQ background worker process |
| `make test` | Run full pytest test suite (includes purity gate & integration tests) |
| `make ruff` | Format and lint Python code with Ruff |
| `make check` | Run static type checking with Mypy |
| `make api-types` | Export OpenAPI schema and generate frontend TypeScript types offline |
| `make migrate` | Apply all database migrations |
| `make create-migration DESC="msg"` | Autogenerate a new database migration |

---

## Advanced Capabilities Inherited from `dut-ai-data-platform`

### 1. Standardized Pagination & Search (`core/pagination/`)
Every collection endpoint follows a universal pagination contract:
- **`PaginationParams`**: `page: int = 1`, `page_size: int = 20` (capped at 100), `search: str | None = None`.
- **`PaginatedResponse[T]`**: `{ items: list[T], total: int, page: int, page_size: int, total_pages: int }`.
- **SQLAlchemy Helper**: `paginate_query(session, stmt, params)` executes database-level `LIMIT`/`OFFSET` and optimized `func.count()`.
- Example endpoint: `GET /api/v1/auth/users?page=1&page_size=10&search=john`.

### 2. Transactional Outbox Event Processor (`core/events/`)
Reliable at-least-once domain event dispatching without external brokers:
- Use cases record domain entities and `OutboxEventModel` inside the same database transaction.
- **`OutboxProcessor`**: Scans pending events, invokes registered async handlers (e.g. `user.registered`), updates status to `PROCESSED`, or tracks failures with `retry_count` and `error_message`.
- Seamlessly driven by the ARQ worker process (`apps/worker/main.py`).

### 3. Frontend Next.js Feature-First Auth & Protected Layout
- **Axios Client (`web/src/lib/api.ts`)**: Pre-configured with `withCredentials: true` and a 401 response interceptor that automatically redirects unauthenticated users to `/login`.
- **Global Auth Context (`web/src/contexts/auth-context.tsx`)**: Backed by TanStack Query (`useUserQuery`), providing `user`, `isLoading`, `login`, `register`, and `logout`.
- **Feature-First Structure (`web/src/features/auth/`)**: Cleanly organized into `components/` (React Hook Form + Zod), `hooks/`, `services/`, and `types/`.
- **Protected Layout (`web/src/app/(protected)/layout.tsx`)**: Route guard preventing unauthorized access to `/dashboard`.

### 4. Production Multi-Stage Dockerfile & CI/CD
- **Backend `Dockerfile`**: 2-stage build with `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` for compiling dependencies and minimal `python:3.12-slim-bookworm` runtime executing under unprivileged user `appuser`.
- **Frontend `web/Dockerfile`**: Standalone Next.js multi-stage build.
- **GitHub Actions (`.github/workflows/ci.yml`)**: Automated pipeline verifying `ruff format`, `ruff check`, `mypy`, `pytest`, contract drift check (`make api-types`), and Next.js TypeScript typecheck.

### 5. DUT-AI True SSO (Single Sign-On) & App Launcher (Waffle)
- **Shared Cookie Domain**: Đăng nhập một lần dùng cho toàn bộ hệ sinh thái `*.dutai.io.vn` qua cookie `access_token` và `refresh_token` tại domain `.dutai.io.vn`.
- **Central IdP**: Kết nối trực tiếp Identity Provider `https://manage.dutai.io.vn/api/v1/auth/me` lấy thông tin định danh và phân quyền RBAC (`role_names`, `permissions`).
- **Edge Middleware (`web/src/middleware.ts`)**: Tự động chuyển hướng người dùng chưa đăng nhập sang `https://workspace.dutai.io.vn/login?redirect=...`.
- **Đồng bộ Đăng xuất (Single Sign-Out)**: `/api/auth/logout` xóa cookie dùng chung trên `.dutai.io.vn` và điều hướng về Workspace Hub.
- **Waffle Menu 9-chấm (`web/src/components/common/DutaiWaffle.tsx`)**: Tích hợp Google-style App Launcher của hệ sinh thái DUT AI vào Header ứng dụng.


