# Phase 0 Research: Boilerplate Advanced Capabilities

## Overview
This document outlines research and technical decisions for integrating four advanced capabilities from `dut-ai-data-platform` into `project-boilerplate`:
1. `OutboxProcessor` event dispatcher
2. Frontend Next.js Feature-First Auth Context & Protected Layout
3. Generic Pagination Abstraction (`core/pagination`)
4. Production Multi-Stage Dockerfile & CI/CD Pipeline

---

## Decision 1: Transactional Outbox Event Processor

### Decision
Implement `OutboxProcessor` in `core/events/processor.py` supporting an in-memory handler registry (`register_handler(event_type, handler)`) and batch execution (`process_pending_batch(session, limit)`).

### Rationale
- **Decoupled Transactions**: Domain use cases write business entities and outbox events within the same local database transaction. If the transaction rolls back, no rogue event is dispatched.
- **At-Least-Once Delivery**: The background worker continuously scans for events where `status = "PENDING"`, invokes all subscribed handlers, and updates status to `PROCESSED` or `FAILED` with retry tracking.
- **Zero External Broker Dependency**: Runs directly against PostgreSQL/SQLite and Redis/ARQ without requiring Kafka or RabbitMQ.

---

## Decision 2: Frontend Auth Context & Route Guarding

### Decision
Structure frontend authentication under `web/src/features/auth/` (types, services, hooks, components) backed by a global `AuthProvider` in `web/src/contexts/auth-context.tsx` and an Axios interceptor in `web/src/lib/api.ts`.

### Rationale
- **Single Source of Truth**: `AuthProvider` uses TanStack Query (`useUserQuery`) to cache the active user profile, eliminating redundant `/me` calls across components.
- **Automatic 401 Interception**: When any protected API call returns HTTP 401 Unauthorized, the response interceptor automatically redirects the browser to `/login` (except on login attempts).
- **Protected Layout**: `web/src/app/(protected)/layout.tsx` guarantees that child routes (like `/dashboard`) are inaccessible to unauthenticated visitors while showing a smooth loading indicator during session verification.

---

## Decision 3: Standardized Pagination, Search & Filtering

### Decision
Provide generic schemas `PaginationParams` and `PaginatedResponse[T]` in `core/pagination/` alongside a reusable SQLAlchemy helper `paginate_query(session, select_stmt, params)`.

### Rationale
- **Universal Contract**: Every collection endpoint across all current and future modules returns `{ items, total, page, page_size, total_pages }`.
- **Performance**: The SQLAlchemy helper applies `LIMIT` and `OFFSET` at the database engine level and executes an optimized count query using `func.count()`.
- **Validation**: Enforces `page >= 1` and `1 <= page_size <= 100`, preventing denial-of-service queries from requesting millions of rows.

---

## Decision 4: Production Multi-Stage Dockerfile with `uv`

### Decision
Create a 2-stage Dockerfile:
1. `builder`: Uses `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`, compiles dependencies via `uv sync --frozen --no-dev`.
2. `runner`: Uses `python:3.12-slim-bookworm`, copies the virtual environment from builder, creates a dedicated non-root user `appuser`, and runs uvicorn.

### Rationale
- Minimal image footprint (~150MB compared to >1GB for standard monolithic builds).
- Security compliance by running without root privileges.
- Fast build caching through dependency layer isolation.

---

## Decision 5: CI/CD Pipeline & Contract Drift Detection

### Decision
Configure GitHub Actions in `.github/workflows/ci.yml` running code quality gates, test suites, and an automated check verifying that `make api-types` produces zero git diffs.

### Rationale
- Prevents breaking changes in backend DTOs from escaping into production without updated frontend types.
- Ensures all team members adhere to `ruff`, `mypy`, and pytest gates automatically on every pull request.
