<!--
SYNC IMPACT REPORT
- Version Change: None (Initial Draft) → 1.0.0
- Modified Principles: Initial ratification of core principles
  - I. Clean Architecture & Domain Purity (NON-NEGOTIABLE)
  - II. Modular Monolith with Dishka IoC
  - III. Transactional Outbox Pattern & Event-Driven Processing
  - IV. Offline Contract & Type Synchronization
  - V. Standardized DUT-AI SSO Integration
- Added Sections:
  - Technical Constraints & Standards
  - Development & Quality Gates
  - Governance
- Removed Sections: None
- Follow-up TODOs: None
-->

# Project Boilerplate Constitution

## Core Principles

### I. Clean Architecture & Domain Purity (NON-NEGOTIABLE)
Entities located in `modules/*/domain/entities.py` MUST be pure Python dataclasses without external framework dependencies.
Domain models MUST NOT import framework or persistence libraries (such as `pydantic`, `fastapi`, `sqlalchemy`, or HTTP clients).
Business rules, domain invariants, and core domain calculations MUST reside exclusively within the domain layer or application services, never inside route handlers, controller scripts, or database ORM models.
This invariant is enforced by automated test suite gates (`tests/test_clean_architecture_purity.py`).

*Rationale*: Keeping business rules completely decoupled from delivery mechanisms and persistence infrastructure guarantees frictionless testability without mocking DB/HTTP layers and shields core domain models from framework churn or breaking deprecations.

### II. Modular Monolith with Dishka IoC
The application is structured as a modular monolith where each distinct bounded context resides in its own isolated package under `modules/<context>/`.
Modules MUST NOT directly import or instantiate internal concrete services or repositories of another module. Cross-module collaboration MUST occur through exported service interfaces, public application DTOs, or asynchronous domain events.
Dependency injection MUST be managed exclusively via Dishka. Every module MUST expose a Dishka `Provider` specifying container bindings with explicit scopes (`Scope.REQUEST` for database sessions and unit of work, `Scope.APP` for singletons and shared client pools).

*Rationale*: Enforcing strict modular encapsulation prevents circular dependencies and architectural decay while preserving the simplicity, rapid iteration, and transactional guarantees of a unified codebase.

### III. Transactional Outbox Pattern & Event-Driven Processing
Cross-module state synchronization, notifications, and long-running background tasks MUST NOT run inline inside the HTTP request-response cycle.
Domain events and asynchronous jobs MUST be persisted to an `outbox` table within the same database transaction that updates business state.
Asynchronous background workers (powered by ARQ and Redis) MUST poll and process outbox messages with at-least-once delivery semantics and idempotent handlers.

*Rationale*: Guaranteeing atomic persistence of state and events eliminates distributed transaction failure modes (the dual-write hazard) and provides resilient, auditable background processing.

### IV. Offline Contract & Type Synchronization
The backend FastAPI application is the single authoritative source of truth for the API contract.
API request and response schemas MUST be defined using Pydantic v2 models.
Frontend TypeScript API types MUST be synchronized directly from the backend schema using the offline generation pipeline (`make api-types`).
Developers MUST NOT manually author parallel TypeScript interfaces for backend API payloads. All frontend network operations MUST use typed client wrappers and TanStack Query / Axios.

*Rationale*: Eliminates runtime contract drift between frontend and backend while removing the requirement to run live backend server processes during frontend code generation or CI validation.

### V. Standardized DUT-AI SSO Integration
External single sign-on authentication MUST interface with the DUT-AI Workspace Identity Provider via `DutAiSsoService`.
The SSO service MUST be configured via environment variables (`SSO_DUTAI_BASE_URL`, defaulting to `https://manage.dutai.io.vn`) and must handle remote token validation gracefully.
All SSO request payloads and response models MUST be strongly typed using Pydantic DTOs (`SsoLoginDataDTO`, `SsoUserDataDTO`); raw dictionary data structures are strictly prohibited.
Remote authentication MUST seamlessly integrate with local identity fallback: users validated via SSO are mapped or provisioned into local identity contexts with appropriate role mappings.

*Rationale*: Centralizes enterprise single sign-on across the DUT-AI ecosystem while decoupling implementation details and preserving strict type safety across all auth boundaries.

## Technical Constraints & Standards

### Backend Stack
- **Runtime**: Python 3.12+ managed via `uv`.
- **Framework**: FastAPI with asynchronous ASGI handlers.
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async engine via `asyncpg`) and Alembic migrations.
- **Dependency Injection**: Dishka with structured `Provider` architecture.
- **Task Queue & Caching**: Redis with ARQ workers.
- **Quality Tooling**: Ruff (linting and formatting) and Mypy (strict static type analysis).

### Frontend Stack
- **Runtime**: Node 22 LTS managed via `pnpm` (with `pnpm-workspace.yaml` allowing native builds).
- **Framework**: Next.js 16 (App Router) with React 19.
- **Styling**: Tailwind CSS v4 and Radix UI / shadcn accessible design patterns.
- **State & Data Fetching**: TanStack React Query with Axios client and centralized 401 interception.
- **API Boundary**: Pure client Next.js application (no Next.js route handlers `app/api/`; all API interactions route directly to FastAPI `/api/v1`).
- **Quality Tooling**: TypeScript compiler (`tsc --noEmit`) and ESLint.

### Infrastructure & Security
- **Containerization**: Multi-stage Docker builds for API, Worker, and Web services with non-root security contexts (`appuser`, UID 10001).
- **Environment Management**: Layered configuration through `.env` files with Pydantic `BaseSettings`. Secrets MUST never be committed to source control.

## Development & Quality Gates

All pull requests and code modifications MUST satisfy the following quality gates prior to merging:
1. **Linting & Formatting**: `make lint` (Ruff check and format inspection).
2. **Static Type Checking**: `make check` (Mypy backend analysis and `pnpm typecheck` frontend validation).
3. **Automated Testing**: `make test` (Pytest test suite, including clean architecture purity tests).
4. **Pre-Commit Enforcement**: Automated verification of formatting, linting, type checking, and secret scanning via `.githooks/pre-commit`.
5. **Contract Synchronization**: Running `make api-types` whenever backend schemas or routes are added or modified.

## Governance

- **Constitutional Supremacy**: This Constitution represents the supreme technical standard of the project. Any code, architecture, or design pattern that violates these principles MUST NOT be approved or merged.
- **Amendment Procedure**: Amendments to this document require explicit documentation of rationale, architectural review, and an increment of the constitutional version.
- **Versioning Policy**:
  - **MAJOR**: Breaking architectural changes, removal of core principles, or major shifts in stack invariants.
  - **MINOR**: Adding new principles, architectural patterns, or material expansions of technical standards.
  - **PATCH**: Wording improvements, clarifications, typo corrections, or non-semantic refinements.
- **Compliance Verification**: All architectural design artifacts (`spec.md`, `plan.md`, `tasks.md`) and code reviews MUST explicitly reference and verify compliance with Core Principles I through V.

**Version**: 1.0.0 | **Ratified**: 2026-11-22 | **Last Amended**: 2026-11-22
