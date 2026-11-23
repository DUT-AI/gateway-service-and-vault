# Implementation Plan: Core Security & Gateway Enforcement (Phase 1)

**Branch**: `013-gateway-security-enforcement` | **Date**: 2026-11-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/013-gateway-security-enforcement/spec.md`

## Summary

Implement and activate the runtime Zero-Trust security enforcement pipeline at the Apache APISIX Gateway and Control Plane. Mount and configure the custom Lua plugin `identity-binding-filter` in the APISIX container to enforce mandatory mTLS hardware verification and virtual key binding on all upstream service routes (`/services/{slug}/*`). Extract the requested service slug dynamically to enforce project service allowlist boundaries directly at gateway ingress. Build atomic client device revocation (`RevokeClientUseCase` and `POST /api/v1/gateway/clients/{id}/revoke`) across the backend and frontend (`web/src/features/clients`), ensuring compromised machines or departing employees have both hardware identity and all associated virtual keys immediately invalidated.

## Technical Context

**Language/Version**: Python 3.12+ (Backend managed via `uv`), Lua 5.1/LuaJIT (APISIX custom plugin), TypeScript 5.8+ / Node 22 (Frontend managed via `pnpm`)  
**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy 2.0 (asyncpg), Dishka (IoC container), Pydantic v2, Python `cryptography`
- Gateway: Apache APISIX 3.9.0, OpenResty LuaJIT, `lua-resty-http`
- Frontend: Next.js 16 (App Router), React 19, Tailwind CSS v4, TanStack Query v5, Radix UI primitives (`AlertDialog`, `Badge`, `Button`), Lucide React
**Storage**: PostgreSQL 16 (Tables: `registered_clients`, `virtual_access_keys`, `project_upstream_allowlist`, `upstream_services`), Redis (Gateway cache)  
**Testing**: `pytest` + `pytest-asyncio` for backend integration tests, `curl` for APISIX end-to-end mTLS & ingress checks, `tsc --noEmit` for frontend  
**Target Platform**: Linux containerized infrastructure (Docker Compose), Modern Web Browsers  
**Project Type**: Full-stack modular monolith with API Gateway ingress  
**Performance Goals**:
- Gateway rejection overhead for missing mTLS / invalid key < 5ms
- Gateway verification and upstream forwarding overhead < 15ms p95
- Client revocation execution latency < 200ms
**Constraints**:
- Clean Architecture domain purity (no framework imports in domain entities)
- Zero-Trust fail-closed design: when Control Plane is unreachable or certificates mismatch, return `HTTP 403 Forbidden` / `HTTP 503`
- Fully typed client-side data fetching without manual TypeScript interface authoring

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Clean Architecture & Domain Purity**: PASS. Domain entities (`RegisteredClientEntity`, `VirtualAccessKeyEntity`) remain pure dataclasses. Repositories and use cases reside in application/infrastructure layers.
- **Principle II: Modular Monolith with Dishka IoC**: PASS. `RevokeClientUseCase` and `VerifyIdentityBindingUseCase` are injected via Dishka `Provider` with explicit scopes (`Scope.REQUEST`).
- **Principle IV: Offline Contract & Type Synchronization**: PASS. Schema changes in `gateway_dtos.py` sync to `web/src/types/api.generated.d.ts` via offline generation.
- **Principle V: Standardized DUT-AI SSO**: PASS. Admin user identity is verified via existing SSO token dependencies (`get_current_user_payload`).
- **Principle VIII: Zero-Trust Identity Binding & APISIX Gateway**: PASS. Central focus of this feature: ties cryptographic mTLS client certificates to virtual access keys and enforces project service boundaries at APISIX ingress.

## Project Structure

### Documentation (this feature)

```text
specs/013-gateway-security-enforcement/
├── plan.md              # Implementation Plan
├── research.md          # Phase 0 Research & Technical Decisions
├── data-model.md        # Phase 1 Data Model & Invariants
├── quickstart.md        # Phase 1 Quickstart Validation Guide
├── contracts/           # Phase 1 API Contracts
│   └── gateway-enforcement-api.md
└── tasks.md             # Phase 2 Output (/speckit-tasks command)
```

### Source Code (repository root)

```text
docker-compose.yml              # Mount ./apps/apisix/plugins volume
apps/apisix/
├── conf/config.yaml            # Add extra_lua_path and identity-binding-filter to plugins list
└── plugins/
    └── identity-binding-filter.lua   # Extract service_slug, verify mTLS cert, invoke verify-binding

modules/gateway/
├── domain/
│   └── interfaces.py           # Extend IRegisteredClientRepository with revoke_client
├── dtos/
│   └── gateway_dtos.py         # Add service_slug to VerifyBindingRequest, RevokeClientResponse
├── repository/
│   └── gateway_repository.py   # Implement revoke_client atomic transaction
├── use_cases/
│   ├── revoke_client.py        # New RevokeClientUseCase
│   └── verify_identity_binding.py # Resolve service_slug and enforce project allowlist
├── client/
│   └── apisix_client.py        # Attach identity-binding-filter to upstream service routes
└── di.py                       # Provide RevokeClientUseCase

apps/api/routers/
└── gateway_router.py           # Expose POST /api/v1/gateway/clients/{id}/revoke

web/src/features/clients/
├── services/
│   └── client-service.ts       # Add revokeClient(id)
├── hooks/
│   └── use-clients-queries.ts  # Add useRevokeClientMutation
└── components/
    └── clients-table.tsx       # Add revoke action, confirmation modal, and REVOKED badge
```

## Complexity Tracking

*No constitutional violations identified. Standard architectural patterns applied.*
