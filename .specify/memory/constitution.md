<!--
SYNC IMPACT REPORT
- Version Change: 2.3.0 → 2.4.0
- Bump Rationale: MINOR. Formally codifies 3-Tier SSO RBAC, Project Membership isolation, strict Production SSO verification (zero unverified JWT fallback), explicit Vault creator ACL granting, Self-Issued mTLS Client Ownership, and Batch Mutation standards under Principles V, VI, and VIII.
- Modified Principles:
  - V. Standardized DUT-AI SSO, External User Directory & Redis Caching (Pure SSO) (NON-NEGOTIABLE)
  - VI. Dynamic Vault & Granular Key-Level Access Control (Zero .env Files)
  - VIII. Zero-Trust Identity Binding, Gateway Edge CORS & Proxy Buffer Governance
- Added Sections: None
- Removed Sections: None
- Follow-up TODOs: None
-->

# Secure API Gateway & Dynamic Vault Constitution

## Core Principles

### I. Clean Architecture, Domain Purity, Repository Isolation & Thin Presentation Layer (NON-NEGOTIABLE)
Entities located in `modules/*/domain/entities.py` MUST be pure Python dataclasses without external framework dependencies.
Domain models MUST NOT import framework or persistence libraries (such as `pydantic`, `fastapi`, `sqlalchemy`, `httpx`, or ORM components).
Business rules, domain invariants, and core domain calculations MUST reside exclusively within the domain layer or application services, never inside route handlers, controller scripts, or database ORM models.

**Repository Isolation & Persistence Rules**:
Repository implementations in `modules/*/repository/` MUST strictly observe Single Responsibility and Aggregate Root isolation:
- Each repository file MUST manage a single Aggregate Root or distinct persistence concern; monolithic "God Repositories" combining multiple aggregate roots into one file are strictly forbidden.
- Repositories MUST NOT import Application layer exceptions (`use_cases/exceptions`) or embed workflow orchestration; failure conditions in persistence must be raised via domain or standard infrastructure errors.
- Repositories MUST NOT call `session.commit()` internally. Transaction commit lifecycles belong strictly to the Unit of Work / Request-scoped transaction manager.
- Cross-aggregate relationships and policy bindings (e.g., project-service bindings and quota policies) MUST be abstracted into dedicated repository contracts (`IQuotaPolicyRepository`) rather than overloading individual aggregate repositories.

**Thin Presentation Layer (Router Purity)**:
Route handlers in `apps/api/routers/` MUST operate strictly as thin HTTP adaptors:
- Routers MUST NOT inject repository interfaces (`IRepository`) directly; all data access and operational actions MUST be encapsulated within dedicated Application Use Cases injected via Dishka (`FromDishka[UseCase]`).
- Routers MUST NOT embed business calculations, fallback policy defaults (e.g. default quota limits), or loops orchestrating multiple downstream queries.
- Use Cases MUST execute all business orchestration and return structured Application/Domain DTOs containing complete, pre-computed data ready for direct mapping to HTTP response schemas.
- Route definitions spanning multiple distinct operational sub-concerns (e.g., projects, clients, keys, services, audit) MUST be modularized into dedicated sub-router modules within a package rather than aggregated into single monolithic files.

This invariant is enforced by automated test suite gates (`tests/test_clean_architecture_purity.py`) and code review checks.

*Rationale*: Keeping business rules and query orchestration completely decoupled from delivery mechanisms and persistence infrastructure guarantees frictionless testability without mocking DB/HTTP layers, shields core domain models from framework churn, prevents presentation layer degradation, and preserves atomic transaction boundaries across distinct aggregates.

### II. Modular Monolith with Dishka IoC
The application is structured as a modular monolith where each distinct bounded context resides in its own isolated package under `modules/<context>/` (including `identity`, `vault`, and `gateway`).
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

### V. Standardized DUT-AI SSO, External User Directory & Redis Caching (Pure SSO) (NON-NEGOTIABLE)
External single sign-on authentication MUST interface exclusively with the central DUT-AI Identity Provider (`https://manage.dutai.io.vn`).
The platform MUST NOT store user passwords, password hashes, or manage independent local user accounts in its database. Local database tables, ORM models, and repositories for user persistence are strictly forbidden; the `identity` bounded context MUST operate with zero local database persistence tables.
User identity context MUST be extracted directly from validated SSO tokens (`Authorization: Bearer` or `access_token` cookie). Unverified offline JWT decoding (`verify_signature=False`) is strictly forbidden outside automated Pytest harnesses (`PYTEST_CURRENT_TEST`); production and runtime environments MUST verify every token against the central SSO IdP.
Authorization MUST follow the standardized **3-Tier Role-Based Access Control (RBAC)** hierarchy resolved from verified SSO claims (`role_names`, `permissions`):
1. `ADMIN` (`admin`, `system`, `superuser`, or `*` permission): Full platform and project governance.
2. `PROJECT_DEVELOPER` (`Project Developer`): Project-membership scoped access (`project_members`), full secret read/write and key/client management within assigned projects.
3. `OTHER` (`Trainer`, `Content`, and unmapped roles): Project-membership scoped read-only project access with key-filtered Vault access.
Client-supplied headers (`X-Identity-Id`, `X-User-Role`) MUST NEVER override authenticated SSO user context.
User directory lookups (options listing and profile inspection) MUST delegate directly to the external user directory service via `IExternalUserDirectoryService` (`GET /api/v1/users/options` and `GET /api/v1/users/{id}`).
To optimize query latency and protect central IdP availability, the service layer MUST cache external user directory responses in Redis (e.g. `identity:users:options` and `identity:users:detail:{user_id}`) with:
- Configurable TTL (default 300 seconds).
- Resilient fail-open behavior (Redis failures MUST NOT block incoming user requests; the service MUST fallback to direct IdP queries gracefully).
- Event-driven cache invalidation triggered upon SSO user revocation or administrative purge.
User identifiers MUST be strictly represented and processed as native integers (`id: int`) across all domain entities, DTOs, endpoint parameters (`id: int = Path(..., ge=1)`), and database foreign keys; string type-coercion workarounds are strictly prohibited.

*Rationale*: Centralizes enterprise identity lifecycle management, eliminates credential compromise risk in the local database, shields the central IdP from redundant high-frequency polling through resilient caching, and enforces strict typing integrity across all bounded contexts.

### VI. Dynamic Vault & Granular Key-Level Access Control (Zero .env Files)
Secrets and environment configurations MUST NOT be stored in plaintext `.env` files on developer machines, production hosts, or committed to version control.
Secrets at rest MUST be encrypted with authenticated `AES-256-GCM` using environment-specific master keys and cryptographic versioning.
Access to secrets MUST be governed by **Project Membership (`project_members`)** and granular **key-level permissions (`key_permissions`)**:
- `ADMIN` users have unrestricted secret access across all projects; `PROJECT_DEVELOPER` users have full-project secret read/write access within their assigned projects.
- `OTHER` roles (`Trainer`, `Content`, etc.) and machine clients/SDKs (`X-Identity-Id`) MUST be strictly filtered by `key_permissions` (`READ`/`WRITE`). When an `OTHER` user creates a secret, permission MUST be granted explicitly via `grant_to_identity_id` driven by `RoleTier`, never via hardcoded `"admin"` or `"system"` actor string checks.
- Multi-item creations (batch secrets, batch project member assignments) MUST use single-transaction batch endpoints rather than N sequential client API calls.
Client SDKs (`dut-vault-sdk`) MUST inject secrets directly into process memory (`os.environ`) at runtime, maintaining a zero-disk invariant.

*Rationale*: Eliminates secret leakage vectors via filesystem snapshots or chat channels while ensuring least-privilege access where team members only access secrets necessary for their explicit responsibilities.

### VII. Real-Time In-Memory Hot-Reload (< 5s Latency)
When configuration secrets are created, updated, or revoked, running application processes MUST receive updates in real time without requiring service restarts.
Secret modifications MUST publish events via Redis Pub/Sub, fanned out to connected clients through Server-Sent Events (SSE) on `GET /api/v1/vault/stream`.
The SSE stream dispatcher MUST perform per-client key-level permission filtering: clients MUST only receive events containing keys they are authorized to access.
SDKs MUST update in-memory configurations and trigger registered reload callbacks within a target latency of under 5 seconds.

*Rationale*: Zero-downtime configuration updates enable immediate secret rotation during security incidents and seamless development without operational disruptions.

### VIII. Zero-Trust Identity Binding, Gateway Edge CORS & Proxy Buffer Governance
All external traffic to backend services MUST route through Apache APISIX operating as a Zero-Trust API Gateway.
Clients MUST present both a valid Virtual Access Key (`X-Virtual-Key`) and a cryptographic client certificate (mTLS for Device Identity or Machine Identity issued by the internal CA).
The gateway MUST enforce Identity Binding via high-performance custom Lua filter (`identity-binding-filter`), verifying the certificate fingerprint against Redis mappings in under 2ms. If a key is copied to an uncertified machine or mismatched project, the gateway MUST fail closed and return `HTTP 403 Forbidden`.
The gateway MUST inject real upstream credentials into forwarded requests, shielding underlying service credentials from downstream clients.

**Self-Issued mTLS Client Ownership**:
- All mTLS client registrations (`POST /api/v1/gateway/clients`) MUST unconditionally lock `owner_id` to the authenticated SSO `user_id` (`ADMIN` and `PROJECT_DEVELOPER`), prohibiting creating certificates on behalf of other users or spoofing `owner_id`.
- `PROJECT_DEVELOPER` users MUST only list and revoke their own mTLS clients (`owner_id == str(user_id)`); cross-user revocation MUST fail with `HTTP 403 Forbidden`. `ADMIN` retains system-wide visibility and revocation governance.

**Edge CORS & Proxy Buffer Governance**:
- The API Gateway MUST terminate and approve cross-origin preflight `OPTIONS` requests at the edge via the native `cors` plugin across all unified routes (`/api/*`), guaranteeing uniform header exchange and eliminating browser `405 Method Not Allowed` or `Network Error` blocks.
- The API Gateway proxy buffer configuration MUST allocate sufficient capacity (`proxy_buffer_size 64k;`, `proxy_buffers 4 64k;`, `proxy_busy_buffers_size 128k;`) to handle cryptographically signed enterprise tokens and authentication headers without upstream truncation or `502 Bad Gateway` drops.

*Rationale*: Mitigates token theft and replay attacks by tying cryptographic possession of client hardware/deployment certificates to API access credentials, centralizes upstream security governance, and ensures resilient edge routing for high-entropy enterprise authentication payloads.

## Technical Constraints & Standards

### Backend Stack
- **Runtime**: Python 3.12+ managed via `uv`.
- **Framework**: FastAPI with asynchronous ASGI handlers.
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async engine via `asyncpg`) and Alembic migrations.
- **Dependency Injection**: Dishka with structured `Provider` architecture.
- **Task Queue & Caching**: Redis with ARQ workers and Redis Pub/Sub.
- **Cryptography & PKI**: Python `cryptography` (AES-256-GCM for Vault secrets; X.509 Private CA for mTLS client certificates).
- **Quality Tooling**: Ruff (linting and formatting) and Mypy (strict static type analysis).

### Gateway & Reverse Proxy Stack
- **Engine**: Apache APISIX 3.x with etcd metadata storage.
- **TLS Termination**: mTLS with client certificate verification via custom CA certificate authority.
- **Custom Plugins**: `identity-binding-filter` Lua plugin for atomic fingerprint and virtual key validation against Redis cache.
- **Upstream Protection**: Credential injection via `proxy-rewrite` plugin and rate limiting via `limit-count`.
- **Edge Routing & Buffers**: Native `cors` plugin active on control plane routes and 64k proxy buffer allocation in `nginx_config`.

### Client SDKs Stack
- **Python SDK**: `packages/dut-vault-sdk` providing synchronous and asynchronous in-memory secret loaders.
- **Hot-Reload Listener**: Background SSE stream listener with automatic reconnection and in-memory dict/env patching.

### Frontend Stack
- **Runtime**: Node 22 LTS managed via `pnpm` (with `pnpm-workspace.yaml` allowing native builds).
- **Framework**: Next.js 16 (App Router) with React 19.
- **Styling**: Tailwind CSS v4 and Radix UI / shadcn accessible design patterns.
- **State & Data Fetching**: TanStack React Query with Axios client and centralized 401 interception.
- **API Boundary**: Pure client Next.js application (no Next.js route handlers `app/api/`; all API interactions route directly to FastAPI `/api/v1` via Gateway).
- **Quality Tooling**: TypeScript compiler (`tsc --noEmit`) and ESLint.

### Infrastructure & Security
- **Containerization**: Multi-stage Docker builds for API, Worker, APISIX, and Web services with non-root security contexts (`appuser`, UID 10001).
- **Environment Management**: Dynamic Vault injection for runtime secrets. Base operational configuration layered through `.env` files with Pydantic `BaseSettings`. Secrets MUST never be committed to source control.

## Development & Quality Gates

All pull requests and code modifications MUST satisfy the following quality gates prior to merging:
1. **Linting & Formatting**: `uv run ruff check --fix && uv run ruff format` (zero linting errors, 100% formatted).
2. **Static Type Checking**: `make check` (Mypy backend analysis and `pnpm typecheck` frontend validation).
3. **Automated Testing**: `uv run pytest` (Pytest test suite, including clean architecture purity tests, with 100% pass rate).
4. **Pre-Commit Enforcement**: Automated verification of formatting, linting, type checking, and secret scanning via `.githooks/pre-commit`.
5. **Contract Synchronization**: Running `make api-types` whenever backend schemas or routes are added or modified.

## Governance

- **Constitutional Supremacy**: This Constitution represents the supreme technical standard of the project. Any code, architecture, or design pattern that violates these principles MUST NOT be approved or merged.
- **Amendment Procedure**: Amendments to this document require explicit documentation of rationale, architectural review, and an increment of the constitutional version.
- **Versioning Policy**:
  - **MAJOR**: Breaking architectural changes, removal of core principles, major shifts in stack invariants, or deprecation of critical identity patterns.
  - **MINOR**: Adding new principles, architectural patterns, or material expansions of technical standards.
  - **PATCH**: Wording improvements, clarifications, typo corrections, or non-semantic refinements.
- **Compliance Verification**: All architectural design artifacts (`spec.md`, `plan.md`, `tasks.md`) and code reviews MUST explicitly reference and verify compliance with Core Principles I through VIII.

**Version**: 2.4.0 | **Ratified**: 2026-11-22 | **Last Amended**: 2026-11-25
