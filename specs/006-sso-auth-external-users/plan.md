# Implementation Plan: SSO-Only Authentication & External User Directory

**Branch**: `006-sso-auth-external-users` | **Date**: 2026-11-23 | **Spec**: [specs/006-sso-auth-external-users/spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/006-sso-auth-external-users/spec.md)

**Input**: Feature specification from `specs/006-sso-auth-external-users/spec.md`

## Summary

Refactor identity and authentication to operate strictly through the central DUT-AI SSO Identity Provider (`https://manage.dutai.io.vn`), completely eliminating local user account credentials and password management from the local database. User directory lookups (`GET /api/v1/users/options` and `GET /api/v1/users/{id}`) are delegated directly to the remote central service, strictly preserving integer identifiers (`id: int`) across all domain models, schemas, and API routes without type coercion workarounds.

## Technical Context

**Language/Version**: Python 3.12+ managed via `uv`  
**Primary Dependencies**: FastAPI, HTTPX (async client), Dishka (DI), Pydantic v2  
**Storage**: Remote DUT-AI Manage IdP via HTTP/REST; zero local user password persistence  
**Testing**: `pytest` with `pytest-asyncio` and `httpx.AsyncClient`  
**Target Platform**: Linux server / macOS / Docker  
**Project Type**: Modular Monolith Backend Web Service  
**Performance Goals**: Sub-second remote directory lookups (< 1s under normal network conditions)  
**Constraints**: Zero local passwords stored, strict integer user IDs (`id: int`), zero framework imports in domain layer  
**Scale/Scope**: Organization-wide SSO authentication, all registered organization members  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle I: Clean Architecture & Domain Purity**: Domain entities in `modules/identity/domain/entities.py` (`ExternalUserOptionEntity`, `ExternalUserDetailEntity`) are pure dataclasses with zero framework imports.
- [x] **Principle II: Modular Monolith with Dishka IoC**: External user directory client is injected via Dishka `IdentityProvider`. No direct cross-module coupling.
- [x] **Principle III: Transactional Outbox Pattern**: N/A for read and SSO proxy operations.
- [x] **Principle IV: Offline Contract & Type Synchronization**: All request/response payloads are defined with strict Pydantic v2 schemas (`id: int`).
- [x] **Principle V: Standardized DUT-AI SSO Integration**: Central SSO authentication uses `DutAiSsoService` communicating with `https://manage.dutai.io.vn`.

## Project Structure

### Documentation (this feature)

```text
specs/006-sso-auth-external-users/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── external-users-api.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code Layout

```text
apps/api/routers/
├── auth_router.py              # SSO-only authentication routes (/sso-login, /me, /logout)
└── user_router.py              # User directory routes (/users/options, /users/{id:int})

modules/identity/
├── domain/
│   ├── entities.py             # Pure dataclasses: ExternalUserOptionEntity, ExternalUserDetailEntity (id: int)
│   └── interfaces.py           # Protocol: IExternalUserDirectoryService
├── dtos/
│   ├── auth_dtos.py            # Token and SSO DTOs
│   └── user_dtos.py            # UserOptionResponse, UserDetailResponse (id: int)
├── services/
│   ├── sso_service.py          # DutAiSsoService (SSO login, me profile)
│   └── external_user_service.py# ExternalUserDirectoryService (options, get_by_id)
├── use_cases/
│   ├── get_user_options.py     # GetUserOptionsUseCase
│   ├── get_user_detail.py      # GetUserDetailUseCase
│   └── __init__.py             # Cleanly exported use cases
└── di.py                       # Dishka IdentityProvider wiring

tests/
├── integration/
│   └── test_external_users_api.py # Integration test verifying SSO auth & external user queries
└── unit/
    └── test_external_user_use_cases.py # Unit tests with mocked external directory service
```

**Structure Decision**:
Keep identity functionality within `modules/identity/` and route definitions in `apps/api/routers/`. Split routes cleanly: `auth_router.py` handles SSO session management, while `user_router.py` exposes directory lookups (`/api/v1/users/options` and `/api/v1/users/{id}`).

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| None | N/A | Fully adheres to Constitution Principles I through V |
