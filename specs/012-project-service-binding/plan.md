# Implementation Plan: Project Upstream Service Binding & Quota Governance

**Branch**: `012-project-service-binding` | **Date**: 2026-11-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/012-project-service-binding/spec.md`

## Summary

Implement end-to-end resource governance allowing project administrators to bind upstream catalog services (e.g., OpenAI, VNPay) to specific projects and configure traffic quota policies (rate limit RPM and daily request cap). Enforce zero-trust authorization at the API gateway so that project virtual access keys can only reach upstream services explicitly authorized for their project. Provide an intuitive frontend workspace tab ("Dịch vụ liên kết") in `/projects/[id]` for seamless auditing, service binding, and instant access revocation.

## Technical Context

**Language/Version**: Python 3.12+ (Backend managed via `uv`), TypeScript 5.8+ / Node 22 (Frontend managed via `pnpm`)
**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy 2.0 (asyncpg), Dishka (IoC container), Pydantic v2
- Frontend: Next.js 16 (App Router), React 19, Tailwind CSS v4, TanStack Query v5, Radix UI primitives, Lucide React
**Storage**: PostgreSQL 16 (Relational tables: `project_upstream_allowlist`, `quota_policies`, `projects`, `upstream_services`), Redis (gateway mapping cache)
**Testing**: `pytest` + `pytest-asyncio` for backend, `tsc --noEmit` and Jest/testing-library for frontend
**Target Platform**: Linux / macOS containerized deployment, Modern Browsers (Chrome, Firefox, Safari)
**Project Type**: Full-stack modular monolith web service
**Performance Goals**:
- Gateway allowlist verification < 2ms latency overhead
- Service binding / revocation UI updates < 200ms
**Constraints**:
- Clean Architecture domain purity (no framework imports in domain entities)
- Zero-Trust Identity Binding (fail closed with HTTP 403 when service not in project allowlist)
- Fully typed client-side data fetching without manual TypeScript interface authoring

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Clean Architecture & Domain Purity**: PASS. Domain entities (`ProjectEntity`, `UpstreamServiceEntity`, `QuotaPolicyEntity`) remain pure dataclasses. Repositories and use cases reside in application/infrastructure layers.
- **Principle II: Modular Monolith with Dishka IoC**: PASS. All services and repositories are wired through `modules/gateway/di.py` with explicit scopes (`Scope.REQUEST`).
- **Principle IV: Offline Contract & Type Synchronization**: PASS. FastAPI models define Pydantic DTOs; frontend types generated via `make api-types`.
- **Principle V: Standardized DUT-AI SSO**: PASS. User context extracted from existing JWT tokens, strict integer IDs for user actors.
- **Principle VIII: Zero-Trust Identity Binding & Gateway**: PASS. Enforces project service allowlist so project keys cannot be abused for unauthorized upstream APIs.

## Project Structure

### Documentation (this feature)

```text
specs/012-project-service-binding/
├── plan.md              # Implementation Plan
├── research.md          # Phase 0 Research & Decisions
├── data-model.md        # Phase 1 Data Model & Invariants
├── quickstart.md        # Phase 1 Quickstart Validation Guide
├── contracts/           # Phase 1 API Contracts
│   └── project-services-api.md
└── tasks.md             # Phase 2 Output (/speckit-tasks command)
```

### Source Code (repository root)

```text
modules/gateway/
├── domain/
│   ├── entities.py             # QuotaPolicyEntity, UpstreamServiceEntity
│   └── interfaces.py           # IProjectRepository extension or IProjectServiceBindingRepository
├── dtos/
│   └── gateway_dtos.py         # Request and Response schemas
├── models/
│   ├── project.py              # project_upstream_association table
│   └── quota.py                # QuotaPolicyModel
├── repository/
│   └── gateway_repository.py   # SQL persistence methods for binding & quotas
├── use_cases/
│   ├── bind_service_to_project.py
│   ├── unbind_service_from_project.py
│   ├── list_project_allowed_services.py
│   └── update_project_service_quota.py
├── di.py                       # Dishka container registration
└── routers/
    └── gateway_router.py       # REST endpoints for /projects/{id}/services

web/src/
├── features/
│   └── projects/
│       ├── api/
│       │   └── project-services.ts    # React Query hooks & Axios calls
│       ├── components/
│       │   ├── allowed-services-table.tsx
│       │   ├── bind-service-dialog.tsx
│       │   ├── project-allowed-services-view.tsx
│       │   └── project-workspace-tabs.tsx   # Add "Dịch vụ liên kết" tab
│       └── types/
│           └── index.ts
```

## Complexity Tracking

*No constitutional violations identified. Standard architectural patterns applied.*
