# Implementation Plan: Secure API Gateway & Centralized Dynamic Vault Platform

**Branch**: `003-api-gateway-vault` | **Date**: 2026-11-23 | **Spec**: [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/003-api-gateway-vault/spec.md)

**Input**: Feature specification from `specs/003-api-gateway-vault/spec.md` and Phase 0 Foundation requirements from `docs/ROADMAP.md`.

## Summary

Build an enterprise-grade API Gateway and Centralized Dynamic Vault platform leveraging modern open-source engines while preserving the project's Clean Architecture Modular Monolith invariants:
1. **Infrastructure & Data Plane (Phase 0 Foundation)**: Deploy **Apache APISIX** (with etcd) as the high-performance API Gateway proxy alongside existing PostgreSQL 16 and Redis 7 in `docker-compose.yml`.
2. **Identity & Gateway Control Plane (`modules/gateway/`)**: Manage Projects, Allowed Upstream Services, Registered Clients (User Devices with DUT AI SSO vs App Servers on Docker), and Virtual Access Keys bound strictly 1:1 to `(Registered Client, Project)`. Synchronize routes and consumers to APISIX via its Admin REST API.
3. **Cryptographic Identity Binding Filter**: Deploy an APISIX Lua plugin verifying client mTLS certificate fingerprints (`$ssl_client_fingerprint`) against cached Virtual Access Key ownership in Redis on every request.
4. **Dynamic Vault Module (`modules/vault/`)**: Securely manage configuration secrets grouped by Scope (`Common`, `Financial`, `Auth-Core`) with AES-256-GCM encryption at rest. Enforce RBAC mapped from DUT AI Manage SSO user roles.
5. **Real-time Hot-Reload Push**: Stream configuration updates to running application SDKs within 5 seconds via Redis Pub/Sub and FastAPI Server-Sent Events (SSE), nạp directly into process RAM without writing `.env` files to disk.

---

## Technical Context

**Language/Version**: Python 3.12 (managed via `uv`), TypeScript 5.x (Node.js 22, managed via `pnpm`).

**Primary Dependencies**:
- **Backend API & Framework**: FastAPI (`>=0.115.0`), Dishka (`>=1.4.0`), Pydantic v2 (`>=2.9.0`), Pydantic-Settings (`>=2.4.0`), Uvicorn.
- **Persistence & Cryptography**: SQLAlchemy 2.0 (`>=2.0.0`), Asyncpg (`>=0.29.0`), Alembic (`>=1.13.0`), `cryptography` (`>=43.0.0` for AES-256-GCM, HKDF, and x509 PKI).
- **Data Plane Gateway**: Apache APISIX 3.9+ (Nginx/OpenResty + Lua, etcd 3.5 control store).
- **Caching, Quota & Event Streaming**: Redis 7 (`redis-py>=5.0.0`), ARQ (`>=0.26.0`), `sse-starlette` (FastAPI SSE streaming).
- **Frontend**: Next.js 16 (App Router), React 19, Tailwind CSS v4, TanStack React Query, Axios.

**Storage**: PostgreSQL 16 (Relational state & encrypted secrets), Redis 7 (APISIX atomic quota counters, identity cache, Pub/Sub events), etcd 3.5 (APISIX dynamic routing state).

**Testing**: Pytest (`pytest-asyncio`, `pytest-cov`, `aiosqlite`), Clean Architecture Purity Gate tests (`tests/test_clean_architecture_purity.py`).

**Target Platform**: Linux / macOS development, Docker & Docker Compose containerized orchestration.

**Project Type**: Modular Monolith Backend, Data Plane Gateway Proxy, Next.js Web Dashboard, and Lightweight In-Memory Client SDK.

**Performance Goals**:
- Gateway mTLS + Identity Binding verification overhead < 20ms p95.
- Atomic Rate Limiting precision under 1,000 req/s concurrency.
- In-memory secret hot-reload propagation < 5 seconds.

**Constraints**:
- Strict Fail-Closed posture: Unverified requests or offline control plane states are rejected (HTTP 503/403).
- Zero plaintext `.env` files written to disk across developer workstations or Docker containers.
- Clean Architecture Purity: Domain entities in `modules/*/domain/entities.py` must have ZERO framework dependencies.

---

## Constitution Check

*GATE: Verified against Project Boilerplate Constitution principles.*

| Principle / Rule | Compliance Status | Analysis |
| :--- | :---: | :--- |
| **I. Clean Architecture & Domain Purity** | **PASS** | `modules/gateway/domain/` and `modules/vault/domain/` use pure `@dataclass` entities with no imports of `pydantic`, `fastapi`, or `sqlalchemy`. Tested via purity gate. |
| **II. Modular Monolith with Dishka IoC** | **PASS** | Distinct business boundaries (`modules/gateway` and `modules/vault`), each exporting a Dishka `Provider` (`Scope.APP`, `Scope.REQUEST`) and decoupled use cases. |
| **III. Transactional Outbox Pattern** | **PASS** | Policy changes, key revocations, and secret changes record domain events to the `outbox` table in the same DB transaction, processed by ARQ worker or Redis Pub/Sub. |
| **IV. Offline Contract Synchronization** | **PASS** | Pydantic DTOs define contracts for Gateway and Vault routes. TypeScript interfaces generated via `make api-types` without running server. |
| **V. Standardized DUT-AI SSO Integration** | **PASS** | Authenticates through `DutAiSsoService` (`https://manage.dutai.io.vn`), mapping user identity and roles (`Financial`, `General`) into local scopes. |

---

## Project Structure

### Documentation (this feature)

```text
specs/003-api-gateway-vault/
├── plan.md              # Implementation Plan (this document)
├── research.md          # Technical decisions and architectural rationales
├── data-model.md        # Domain entities, ORM tables, DTO schemas, and lifecycles
├── quickstart.md        # Step-by-step setup and verification guide
├── contracts/           # API contracts, Gateway proxy headers, and SDK protocols
│   ├── gateway-contracts.md
│   ├── vault-contracts.md
│   └── sdk-contract.md
└── checklists/
    └── requirements.md  # Quality verification checklist
```

### Source Code (repository root layout)

```text
gateway-service-and-vault/
├── core/                        # Shared infrastructure
│   ├── config/                  # App, Database, Redis, APISIX, Vault settings
│   ├── security/                # JWT, AES-GCM cipher, x509 PKI utilities
│   ├── database/                # SQLAlchemy async session, base, UoW
│   ├── events/                  # Outbox event publisher & processor
│   └── utils/                   # ULID generator, cryptographic hashing
│
├── modules/
│   ├── identity/                # Reference module (DUT AI SSO user sync)
│   ├── gateway/                 # API Gateway Management Bounded Context
│   │   ├── domain/              # Entities: Project, RegisteredClient, VirtualKey, UpstreamService, QuotaPolicy
│   │   ├── dtos/                # Pydantic schemas for gateway management
│   │   ├── models/              # SQLAlchemy models for gateway tables
│   │   ├── repository/          # SQLAlchemy repositories
│   │   ├── use_cases/           # RegisterClient, GenerateVirtualKey, SyncApisixRoute, RevokeKey
│   │   ├── client/              # APISIX Admin API HTTP Client
│   │   └── di.py                # Gateway Dishka Provider
│   │
│   └── vault/                   # Centralized Dynamic Secrets Bounded Context
│       ├── domain/              # Entities: SecretScope, SecretItem, SecretHistory
│       ├── dtos/                # Pydantic schemas for secret management
│       ├── models/              # SQLAlchemy models for secrets and scopes
│       ├── repository/          # Encrypted secret repository
│       ├── use_cases/           # CreateSecret, GetSecretsByScope, UpdateSecret, StreamUpdates
│       ├── services/            # EncryptionService (AES-256-GCM), SSEBroadcaster
│       └── di.py                # Vault Dishka Provider
│
├── apps/
│   ├── api/                     # FastAPI entrypoint, routers for /api/v1/gateway & /api/v1/vault
│   ├── worker/                  # ARQ background task runner for outbox events
│   └── apisix/                  # APISIX configuration & Custom Lua Plugins
│       ├── conf/apisix.yaml     # Standalone config or etcd bootstrap
│       └── plugins/identity-binding-filter.lua  # mTLS + Virtual Key binding verification
│
├── packages/
│   └── dut-vault-sdk/           # Lightweight Python / Node.js in-memory client runner
│
├── web/                         # Next.js 16 Web Dashboard
│   └── src/features/
│       ├── gateway/             # Projects, Upstream Services, Devices, Quotas
│       └── vault/               # Secrets Management, Scope RBAC, Audit Log
│
├── docker-compose.yml           # PostgreSQL, Redis, MinIO, etcd, APISIX, API, Web, Worker
├── Makefile                     # make dev-api, make dev-web, make migrate, make api-types
└── pyproject.toml
```

**Structure Decision**: Adopts the established Modular Monolith pattern. Extends `core/security/` with cryptographic helpers, adds `modules/gateway/` and `modules/vault/`, and mounts APISIX with etcd in `docker-compose.yml`.

---

## Complexity Tracking

| Component / Pattern | Why Needed | Simpler Alternative Rejected Because |
| :--- | :--- | :--- |
| **Apache APISIX + etcd** | Reverse proxy, high-performance mTLS termination, atomic distributed rate-limiting, and zero-downtime dynamic routing. | Writing a custom Python reverse proxy fails at high concurrency, introduces 100ms+ latency overhead, and cannot handle enterprise mTLS handshakes cleanly. |
| **APISIX Custom Lua Plugin** | Real-time cryptographic identity binding verification directly at the network proxy layer. | Proxying every request through a sidecar FastAPI service introduces 2x network hop latency and negates Nginx throughput advantages. |
| **AES-256-GCM Authenticated Encryption** | Guarantees confidentiality and tampering detection for secrets stored in the central database. | Plaintext database storage violates basic security; Fernet (CBC + HMAC) lacks native hardware-accelerated AES-GCM performance. |
| **Server-Sent Events (SSE) for Hot-Reload** | Pushes secret changes from Control Plane directly to client process RAM in < 5 seconds. | WebSockets are bidirectional and overkill for a push-only notification; HTTP polling creates database load and delayed propagation. |
