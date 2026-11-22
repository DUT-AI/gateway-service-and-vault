# Implementation Plan: Boilerplate Advanced Capabilities (DUT-AI Style)

**Branch**: `002-boilerplate-extensions` | **Date**: 2026-11-22 | **Spec**: [spec.md](file:///Users/nguyenhuynh/Documents/projects/project-boilerplate/specs/002-boilerplate-extensions/spec.md)

**Input**: Feature specification from `specs/002-boilerplate-extensions/spec.md`

## Summary

Incorporate 4 advanced capabilities from `dut-ai-data-platform` into `project-boilerplate`:
1. `OutboxProcessor` in `core/events/processor.py` for asynchronous background event processing.
2. Complete Next.js full-stack integration: `web/src/lib/api.ts` (with 401 interceptor & credentials), `web/src/contexts/auth-context.tsx`, feature-first `web/src/features/auth/` (Login & Register forms with zod), and protected layout `/dashboard`.
3. Standardized pagination and search abstraction (`core/pagination/`) and paginated list endpoint (`GET /api/v1/auth/users`).
4. Production-ready multi-stage `Dockerfile` and automated GitHub Actions CI workflow (`.github/workflows/ci.yml`).

---

## Technical Context

**Language/Version**: Python 3.12 (`uv`), TypeScript 5.x (Node 20+, Next.js 16).

**Primary Dependencies**:
- Backend: FastAPI, Dishka, SQLAlchemy 2.0, Asyncpg, Redis, ARQ, Loguru, Pydantic v2.
- Frontend: Next.js 16, React 19, Tailwind CSS v4, TanStack React Query, Axios, React Hook Form, Zod, Lucide React.

**Storage**: PostgreSQL 16, Redis 7, MinIO.

**Testing**: Pytest, Pytest-Asyncio, Aiosqlite, In-memory test container.

---

## Constitution Check

| Principle / Rule | Compliance Status | Analysis |
|------------------|-------------------|----------|
| **Domain Purity** | **PASS** | Domain entities in `modules/identity` remain pure dataclasses with zero framework dependencies. |
| **Separation of Concerns** | **PASS** | Pagination abstractions reside in `core/pagination`; frontend auth resides in `web/src/features/auth`. |
| **Contract Synchronization** | **PASS** | Paginated DTOs export to OpenAPI and regenerate `api.generated.d.ts`. CI checks enforce zero drift. |

---

## Project Structure

```text
specs/002-boilerplate-extensions/
├── plan.md              # Implementation plan
├── research.md          # Technical decisions
├── data-model.md        # Schemas & DTO definitions
├── quickstart.md        # Validation guide
├── contracts/
│   └── api-contracts.md # API and frontend interceptor contracts
└── checklists/
    └── requirements.md  # Specification checklist

Source Additions:
├── core/
│   ├── events/
│   │   └── processor.py         # OutboxProcessor event dispatcher
│   └── pagination/              # Standardized pagination & search
│       ├── __init__.py
│       ├── params.py            # PaginationParams
│       ├── response.py          # PaginatedResponse[T]
│       └── helpers.py           # paginate_query SQLAlchemy helper
│
├── modules/identity/
│   ├── dtos/auth_dtos.py        # Add pagination schemas
│   ├── repository/              # Add list_users with pagination
│   ├── use_cases/list_users.py  # ListUsersUseCase
│   └── di.py                    # Register ListUsersUseCase
│
├── apps/api/routers/auth_router.py # Add GET /api/v1/auth/users
│
├── web/
│   ├── Dockerfile               # Multi-stage Next.js Dockerfile
│   └── src/
│       ├── lib/api.ts           # Axios client with credentials & 401 interceptor
│       ├── contexts/
│       │   └── auth-context.tsx # AuthProvider & useAuth hook
│       ├── features/auth/       # Feature-first auth
│       │   ├── components/      # LoginForm, RegisterForm
│       │   ├── hooks/           # useUserQuery, useLoginMutation
│       │   ├── services/        # authService
│       │   └── types/           # User, LoginPayload, RegisterPayload
│       └── app/
│           ├── login/page.tsx   # Login page
│           ├── register/page.tsx# Register page
│           └── (protected)/     # Protected route layout & dashboard
│               ├── layout.tsx
│               └── dashboard/page.tsx
│
├── Dockerfile                   # Multi-stage production Dockerfile
└── .github/workflows/ci.yml     # Automated CI pipeline
```

---

## Complexity Tracking

| Component | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| **OutboxProcessor** | At-least-once event delivery | Raw inline worker calls fail silently when network blips occur. |
| **Generic Pagination** | Reusable list responses across all entities | Ad-hoc pagination creates inconsistent contracts across endpoints. |
| **Multi-Stage Dockerfile** | Production security & minimal image size | Single-stage images include build tools and run as root. |
