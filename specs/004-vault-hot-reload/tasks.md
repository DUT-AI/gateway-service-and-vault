---
description: "Task list for Real-Time Dynamic Vault Hot-Reload feature implementation"
---

# Tasks: Real-Time Dynamic Vault Hot-Reload

**Input**: Design documents from `/specs/004-vault-hot-reload/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`  
**Tests**: Included as specified in spec success criteria and validation scenarios.  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`)
- Exact file paths included in all task descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, SDK package structure, and configuration setup

- [X] T001 [P] Ensure Redis client and async connection settings are exposed in `core/config/redis.py`
- [X] T002 [P] Create package directory structure for client SDK in `packages/dut-vault-sdk/dut_vault_sdk/`
- [X] T003 [P] Initialize `packages/dut-vault-sdk/pyproject.toml` with metadata, dependencies (`httpx>=0.27.0`), and CLI entry points

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain entities, broadcaster interface, DTOs, and DI bindings that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Define pure domain entity `ConfigChangeEvent` in `modules/vault/domain/entities.py` with fields: `project_id: str` (non-empty string), `scope_name: str` (non-empty string), `changed_keys: list[str]` (at least 1 key), `new_version: int` (strictly positive integer `>= 1`), `actor: str`, `event_id: str`, and `timestamp: datetime` (UTC)
- [X] T005 [P] Define pure protocol interface `IVaultBroadcaster` in `modules/vault/domain/interfaces.py` with method `async def publish_secret_change(self, event: ConfigChangeEvent) -> None`
- [X] T006 [P] Define Pydantic v2 schemas `SecretUpdateEventPayload` and `StreamPingPayload` in `modules/vault/dtos/vault_dtos.py`
- [X] T007 Implement Redis-backed event broadcaster `RedisVaultBroadcaster` in `modules/vault/services/broadcaster.py` publishing JSON-serialized event payloads to Redis Pub/Sub channel pattern `vault:project:{project_id}:changes`
- [X] T008 Register `IVaultBroadcaster` and `RedisVaultBroadcaster` in `modules/vault/di.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Real-Time Configuration Change Broadcast and Delivery (Priority: P1) 🎯 MVP

**Goal**: Broadcast secret updates immediately (< 1s) across Redis Pub/Sub and stream real-time events over FastAPI SSE to authenticated clients with 15s heartbeat pings and strict project isolation.

**Independent Test**: Connect an SSE client to `GET /api/v1/vault/projects/{id}/stream`. Modify a secret via `POST /api/v1/vault/projects/{id}/secrets`. Verify the SSE stream receives `secret_update` within 1 second.

### Tests for User Story 1

- [X] T009 [P] [US1] Create unit tests for `RedisVaultBroadcaster` in `tests/unit/test_vault_broadcaster.py`
- [X] T010 [P] [US1] Create integration test for SSE streaming endpoint in `tests/integration/test_vault_sse_stream.py` verifying project isolation, 15s heartbeat pings, and event delivery

### Implementation for User Story 1

- [X] T011 [US1] Update `CreateSecretUseCase` in `modules/vault/use_cases/vault_use_cases.py` to inject `IVaultBroadcaster` and publish `ConfigChangeEvent` upon committing secret updates
- [X] T012 [US1] Implement SSE streaming endpoint `GET /api/v1/vault/projects/{project_id}/stream` in `apps/api/routers/vault_router.py` using FastAPI `StreamingResponse` and `redis.asyncio` pubsub listener
- [X] T013 [US1] Add heartbeat ping generator (every 15 seconds) and clean client disconnection handlers in `apps/api/routers/vault_router.py`

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently (MVP ready!)

---

## Phase 4: User Story 2 - In-Memory Configuration Injection and Hot-Reload without Files (Priority: P2)

**Goal**: Provide Python client SDK (`dut-vault-sdk`) and CLI runner that fetches authorized secrets into process RAM, maintains zero plaintext files on disk, and atomically updates memory in < 5 seconds upon receiving SSE change notifications.

**Independent Test**: Launch a sample script using `VaultClient`. Verify variables are in RAM and no `.env` file exists on disk. Update a secret on the API and assert `client.get(...)` reflects the new value within 5 seconds without process restart.

### Tests for User Story 2

- [X] T014 [P] [US2] Create unit tests for `InMemoryConfigStore` in `tests/unit/test_in_memory_config_store.py` asserting thread-safety and change callback execution
- [X] T015 [P] [US2] Create integration tests in `tests/integration/test_sdk_hot_reload.py` asserting < 5s RAM mutation, reconnection logic, and zero-disk file artifact invariant

### Implementation for User Story 2

- [X] T016 [P] [US2] Implement thread-safe `InMemoryConfigStore` in `packages/dut-vault-sdk/dut_vault_sdk/store.py` with `threading.RLock`, atomic bulk updates, `os.environ` sync, and `on_change` callback hooks
- [X] T017 [US2] Implement `VaultClient` in `packages/dut-vault-sdk/dut_vault_sdk/client.py` with REST initial secret fetch, background SSE listener thread, watchdog heartbeat checking, and exponential backoff reconnection
- [X] T018 [US2] Implement CLI runner in `packages/dut-vault-sdk/dut_vault_sdk/__main__.py` supporting `dut-vault run --project=<id> [options] -- <command> [args...]`
- [X] T019 [US2] Export public package interfaces (`VaultClient`, `InMemoryConfigStore`) in `packages/dut-vault-sdk/dut_vault_sdk/__init__.py`

**Checkpoint**: At this point, User Stories 1 AND 2 are fully functional and integrated.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Architectural validation, documentation, and end-to-end quickstart execution

- [X] T020 Verify Clean Architecture purity gate in `tests/test_clean_architecture_purity.py` ensuring zero framework imports in `modules/vault/domain/`
- [X] T021 [P] Update documentation in `docs/ROADMAP.md` and feature docs with SSE streaming and SDK usage
- [X] T022 Execute end-to-end quickstart validation scenarios from `specs/004-vault-hot-reload/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Completed
- **Foundational (Phase 2)**: Completed
- **User Stories (Phase 3+)**: Completed
  - User Story 1 (P1): Completed
  - User Story 2 (P2): Completed
- **Polish (Phase 5)**: Completed
