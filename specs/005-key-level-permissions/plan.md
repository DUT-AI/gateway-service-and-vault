# Implementation Plan: Granular Key-Level Secret Permissions (Identity-to-Key ACL)

**Branch**: `005-key-level-permissions` | **Date**: 2026-11-23 | **Spec**: [specs/005-key-level-permissions/spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/005-key-level-permissions/spec.md)

**Input**: Feature specification from `specs/005-key-level-permissions/spec.md`

## Summary

Implement fine-grained Identity-to-Key access control in Centralized Dynamic Vault, replacing role-based scope heuristics with explicit key authorization:
1. **Database Persistence**: Create `key_permissions` table tracking `(project_id, identity_id, secret_key)` mappings.
2. **Domain & Repositories**: Define pure `KeyPermissionEntity` and extend Vault repository protocols to grant, revoke, check, and list permitted keys per identity.
3. **Application Enforcement**:
   - `GrantKeyPermissionUseCase` / `RevokeKeyPermissionUseCase`.
   - Update `GetSecretsByScopeUseCase` to evaluate caller's permitted keys and return ONLY granted keys in memory.
   - Deny unauthorized single key requests with HTTP 403 Forbidden.
4. **SSE Stream Filtering**: Filter real-time change events based on the connected caller's permitted keys.

---

## Technical Context

**Language/Version**: Python 3.12+ managed via `uv`  
**Primary Dependencies**: FastAPI, Dishka (IoC container), SQLAlchemy 2.0 (asyncpg), Alembic, Pydantic v2  
**Storage**: PostgreSQL (`key_permissions` table with cascade delete and composite index)  
**Testing**: `pytest`, `pytest-asyncio`, SQLite in-memory / test client  
**Target Platform**: Linux / macOS Docker container runtimes & developer workstations  
**Project Type**: Modular Monolith Backend Web Service  
**Performance Goals**: Key permission evaluation overhead < 10ms; Grant/Revoke operations < 50ms  
**Constraints**: Zero framework imports in domain layer (Constitution Principle I); Deny-by-default permission posture  
**Scale/Scope**: Up to 1,000 distinct secret keys per project; instantaneous key-level filtering  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|---|---|---|---|
| **I. Clean Architecture & Domain Purity** | Domain entities in `modules/vault/domain/entities.py` must have zero framework imports (`pydantic`, `fastapi`, `sqlalchemy`). | **PASS** | `KeyPermissionEntity` is a pure Python `@dataclass`. |
| **II. Modular Monolith with Dishka IoC** | No cross-module internal concrete imports; Dishka `Provider` manages dependency injection with explicit scopes. | **PASS** | Repository and use cases bound via `VaultProvider` in `modules/vault/di.py`. |
| **III. Transactional Outbox & Events** | Key permission mutations committed in same database session. | **PASS** | Enforced via AsyncSession and repository layer. |
| **IV. Offline Contract & Type Sync** | Pydantic v2 schemas for all permission endpoints. | **PASS** | `GrantKeyPermissionRequest`, `KeyPermissionResponse`, etc. in `modules/vault/dtos/vault_dtos.py`. |
| **V. Standardized DUT-AI SSO** | Standard auth headers and identity integration (`X-Identity-Id`, `X-Client-Id`). | **PASS** | Extracts caller identity from standard identity propagation headers. |

---

## Project Structure

### Documentation (this feature)

```text
specs/005-key-level-permissions/
├── plan.md              # This file
├── research.md          # Phase 0: Authorization model & caller identity decisions
├── data-model.md        # Phase 1: KeyPermissionEntity, SQLAlchemy model, DTOs
├── quickstart.md        # Phase 1: Runnable validation scenarios
├── contracts/           # Phase 1: Interface contracts
│   └── key-permissions-api.md # API endpoints for permissions and secret retrieval
└── checklists/
    └── requirements.md  # Spec requirements checklist
```

### Source Code (repository root)

```text
modules/vault/
├── domain/
│   ├── entities.py       # KeyPermissionEntity (pure dataclass)
│   └── interfaces.py     # Updated ISecretRepository with key permission methods
├── models/
│   └── permission.py     # KeyPermissionModel SQLAlchemy mapping
├── dtos/
│   └── vault_dtos.py     # GrantKeyPermissionRequest, KeyPermissionResponse, etc.
├── repository/
│   └── secret_repository.py # Implementation of key permission queries
├── use_cases/
│   └── vault_use_cases.py# GrantKeyPermissionUseCase, RevokeKeyPermissionUseCase, updated secret retrieval
└── di.py                 # Dishka VaultProvider bindings

apps/api/
└── routers/
    └── vault_router.py   # Permission endpoints + updated X-Identity-Id secret retrieval & SSE stream

migrations/versions/
└── 003_key_permissions.py # Alembic migration for key_permissions table

tests/
├── unit/
│   └── test_key_permissions_use_cases.py
└── integration/
    └── test_granular_key_permissions.py
```

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| *None* | No constitutional violations. Clean Architecture and modular structure are strictly preserved. | N/A |
