# Implementation Plan: Pure SSO Authentication & Gateway Flow

**Branch**: `018-pure-sso-gateway-auth` | **Date**: 2026-11-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/018-pure-sso-gateway-auth/spec.md`

## Summary

Eradicate browser `Network Error` and authentication stalls by configuring the APISIX Zero-Trust Gateway to handle cross-origin preflight (`OPTIONS`) requests at the edge, uncoupling credential validation from profile hydration on the frontend, and maintaining seamless token persistence across development ports.

## Technical Context

**Language/Version**: Python 3.12 (Backend), TypeScript 5.x / Next.js 16 (Frontend), Lua / APISIX 3.9 (Gateway)

**Primary Dependencies**:
- Backend: FastAPI, Dishka DI, httpx, PyJWT, aioredis
- Frontend: Next.js 16 (App Router), React 19, TanStack Query v5, Axios, React Hook Form, Zod
- Gateway: Apache APISIX 3.9 with `cors` and `identity-binding-filter` plugins

**Storage**: Redis (SSO user directory caching & quota tracking), PostgreSQL (Alembic managed, zero local user tables)

**Testing**: Pytest (backend integration & unit tests), Vitest / TypeScript check (`tsc --noEmit`), ESLint

**Target Platform**: Linux / macOS Docker containerized services with local host port mapping (Frontend :3000, Gateway :9080, Backend :8000)

**Project Type**: Modular monolith with decoupled Next.js web application and APISIX API Gateway

**Performance Goals**:
- Preflight `OPTIONS` response time < 2ms at APISIX edge
- Login to Dashboard redirection < 2 seconds end-to-end
- User profile cache hit latency < 5ms via Redis

**Constraints**:
- Strict adherence to Constitution v2.2.0 Principle V (Zero passwords in database, native integer user IDs)
- Zero-disk secret storage in client and memory

**Scale/Scope**: Enterprise workspace multi-project gateway supporting thousands of daily authenticated API requests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle I (Clean Architecture & Repository Isolation)**: Domain entities remain pure dataclasses. Zero database user models/repositories in `modules/identity`.
- [x] **Principle II (Modular Monolith with Dishka)**: `IdentityProvider` encapsulates directory service and use cases without cross-module coupling.
- [x] **Principle IV (Offline Contract & Type Sync)**: API schemas defined in Pydantic v2 and TypeScript types generated offline.
- [x] **Principle V (Pure SSO & Zero Local Passwords & Redis Caching)**: All auth delegated to DUT-AI IdP; Redis caching implemented for directory lookups; integer IDs enforced.
- [x] **Principle VIII (Zero-Trust Identity Binding & Gateway)**: Traffic routes through APISIX gateway with centralized CORS and identity binding.

## Project Structure

### Documentation (this feature)

```text
specs/018-pure-sso-gateway-auth/
├── plan.md              # This file
├── research.md          # Phase 0: CORS preflight & token storage analysis
├── data-model.md        # Phase 1: Entity schemas and lifecycle states
├── quickstart.md        # Phase 1: Runnable verification guide
├── contracts/           # Phase 1: OpenAPI authentication contract
│   └── sso-auth-api.yaml
└── checklists/          # Quality validation checklists
    └── requirements.md
```

### Source Code (repository root)

```text
apps/
├── api/
│   ├── main.py                          # Lifespan APISIX synchronization & CORS
│   └── routers/
│       └── auth_router.py               # /sso-login, /me, /logout endpoints
└── apisix/
    └── conf/
        └── config.yaml                  # APISIX plugins enabled: cors, identity-binding-filter

modules/
├── gateway/
│   └── client/
│       └── apisix_client.py             # Route sync with native cors plugin
└── identity/
    ├── services/
    │   ├── external_user_service.py     # Redis cached external user queries
    │   └── sso_service.py               # DUT-AI Manage IdP HTTP client
    └── use_cases/                       # Pure SSO application use cases

web/
└── src/
    ├── app/
    │   ├── login/page.tsx               # Pure SSO login screen
    │   └── (protected)/layout.tsx       # Protected dashboard shell
    ├── features/auth/
    │   ├── components/login-form.tsx    # Single-action SSO login form
    │   ├── hooks/use-auth-queries.ts    # Uncoupled login mutation & user query
    │   └── services/auth-service.ts     # Token storage in localStorage & cookie
    ├── lib/
    │   └── api.ts                       # Axios client with Authorization header interceptor
    └── middleware.ts                    # Edge session protection via cookie
```

**Structure Decision**: Retains the established modular monolith layout with dedicated `web` frontend and `apps/apisix` reverse proxy infrastructure.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| None | All designs conform 100% to Constitution v2.2.0 | N/A |
