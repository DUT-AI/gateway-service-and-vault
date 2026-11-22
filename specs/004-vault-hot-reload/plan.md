# Implementation Plan: Real-Time Dynamic Vault Hot-Reload

**Branch**: `004-vault-hot-reload` | **Date**: 2026-11-23 | **Spec**: [specs/004-vault-hot-reload/spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/004-vault-hot-reload/spec.md)

**Input**: Feature specification from `specs/004-vault-hot-reload/spec.md`

## Summary

Deliver a real-time event pipeline for centralized configuration secrets and zero-disk in-memory client SDK hot-reloading:
1. **Event Pipeline**: Upon secret creation/update in `modules/vault`, immediately publish change notifications over Redis Pub/Sub (`vault:project:{project_id}:changes`).
2. **FastAPI SSE Stream**: Expose `GET /api/v1/vault/projects/{project_id}/stream` yielding `secret_update` events and 15s heartbeat `ping`s over standard HTTP Server-Sent Events.
3. **In-Memory SDK (`packages/dut-vault-sdk/`)**: Client runtime package and CLI runner that decrypts secrets directly into process RAM (`InMemoryConfigStore` and `os.environ`), maintaining zero plaintext files on disk and mutating memory within 5 seconds when change notifications arrive.

---

## Technical Context

**Language/Version**: Python 3.12+ managed via `uv`  
**Primary Dependencies**:
- Backend: FastAPI, Dishka (IoC container), `redis.asyncio` (Redis Pub/Sub), SQLAlchemy 2.0 (asyncpg), `cryptography`
- Client SDK: `httpx` (HTTP/SSE client) or standard Python `urllib` / `http.client` with minimal footprint  
**Storage**: PostgreSQL (persisted encrypted secrets), Redis 7 (ephemeral Pub/Sub broker)  
**Testing**: `pytest`, `pytest-asyncio`, SQLite in-memory / mock Redis tests  
**Target Platform**: Linux / macOS Docker container runtimes & developer workstations  
**Project Type**: Modular Monolith Web Service + Client SDK Library/CLI  
**Performance Goals**: Event transmission and RAM mutation latency < 5 seconds (target < 1 second); SSE connection ping interval 15 seconds  
**Constraints**: Zero plaintext `.env` disk artifacts; strict Clean Architecture domain purity (zero framework imports in `domain/`)  
**Scale/Scope**: 100+ concurrent SSE streams per replica; instantaneous fan-out to all subscribed project instances  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|---|---|---|---|
| **I. Clean Architecture & Domain Purity** | Domain entities in `modules/vault/domain/entities.py` must have zero framework imports (`pydantic`, `fastapi`, `sqlalchemy`). | **PASS** | `ConfigChangeEvent` is a pure dataclass; `IVaultBroadcaster` is a pure Python `Protocol`. |
| **II. Modular Monolith with Dishka IoC** | No cross-module internal imports; Dishka `Provider` manages dependency injection with explicit scopes. | **PASS** | `RedisVaultBroadcaster` bound as `Scope.APP` in `modules/vault/di.py`. |
| **III. Transactional Outbox & Events** | Secrets persisted atomically before broadcast; async workers/events decoupled from request cycles. | **PASS** | `CreateSecretUseCase` commits to PostgreSQL repository then triggers broadcaster. |
| **IV. Offline Contract & Type Sync** | Pydantic v2 models for all request/response payloads; types verifiable offline. | **PASS** | `SecretUpdateEventPayload` and stream query DTOs defined in `modules/vault/dtos/vault_dtos.py`. |
| **V. Standardized DUT-AI SSO** | Standard auth headers and identity integration supported. | **PASS** | Stream endpoint respects `X-User-Role` and gateway client identity headers. |

---

## Project Structure

### Documentation (this feature)

```text
specs/004-vault-hot-reload/
├── plan.md              # This file
├── research.md          # Phase 0: Protocol & architecture decisions
├── data-model.md        # Phase 1: Entity & in-memory data models
├── quickstart.md        # Phase 1: Runnable validation guide
├── contracts/           # Phase 1: Interface contracts
│   ├── sse-stream.md    # SSE HTTP endpoint contract
│   └── sdk-interface.md # Python SDK & CLI interface
└── checklists/
    └── requirements.md  # Spec requirements checklist
```

### Source Code (repository root)

```text
modules/vault/
├── domain/
│   ├── entities.py       # Pure dataclass ConfigChangeEvent
│   └── interfaces.py     # Pure protocol IVaultBroadcaster
├── dtos/
│   └── vault_dtos.py     # SecretUpdateEventPayload, StreamPingPayload
├── services/
│   ├── encryption.py     # AES-256-GCM encryption service
│   └── broadcaster.py    # RedisVaultBroadcaster implementing IVaultBroadcaster
├── use_cases/
│   └── vault_use_cases.py# CreateSecretUseCase updated to broadcast on change
└── di.py                 # Dishka VaultProvider binding IVaultBroadcaster

apps/api/
├── routers/
│   └── vault_router.py   # GET /api/v1/vault/projects/{id}/stream endpoint
└── di.py                 # Container configuration

packages/
└── dut-vault-sdk/
    ├── dut_vault_sdk/
    │   ├── __init__.py   # VaultClient export
    │   ├── client.py     # VaultClient implementation (REST fetch + SSE loop)
    │   ├── store.py      # InMemoryConfigStore (thread-safe RAM dictionary)
    │   └── __main__.py   # CLI runner: python -m dut_vault_sdk run -- ...
    └── pyproject.toml    # SDK packaging definition

tests/
├── unit/
│   ├── test_vault_broadcaster.py
│   └── test_in_memory_config_store.py
└── integration/
    ├── test_vault_sse_stream.py
    └── test_sdk_hot_reload.py
```

**Structure Decision**:
- The backend changes cleanly integrate into the existing `modules/vault/` bounded context and `apps/api/routers/vault_router.py`.
- The client SDK is placed under `packages/dut-vault-sdk/` as a modular, distributable Python package and CLI runner that can be imported or executed in standalone environments.

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| *None* | No constitutional violations. Clean Architecture and modular structure are strictly preserved. | N/A |
