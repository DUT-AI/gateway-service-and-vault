# Tasks: Secure API Gateway & Centralized Dynamic Vault Platform

**Input**: Design documents from `/specs/003-api-gateway-vault/`
**Prerequisites**: [plan.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/003-api-gateway-vault/plan.md), [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/003-api-gateway-vault/spec.md), [research.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/003-api-gateway-vault/research.md), [data-model.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/003-api-gateway-vault/data-model.md), [contracts/](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/003-api-gateway-vault/contracts/)

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Phase 0 Foundation Infrastructure & Domain)

**Purpose**: Infrastructure orchestration, configuration settings, and Clean Architecture domain entities.

- [x] T001 Update `docker-compose.yml` to add `etcd:3.5` and `apache/apisix:3.9.0-debian` services with volume mounts
- [x] T002 Create APISIX configuration file `apps/apisix/conf/config.yaml` with etcd endpoint and Admin API key
- [x] T003 [P] Create Pydantic settings `core/config/apisix.py` and `core/config/vault.py` and export in `core/config/__init__.py`
- [x] T004 [P] Implement pure domain entities in `modules/gateway/domain/entities.py` (Zero framework dependencies)
- [x] T005 [P] Implement pure domain entities in `modules/vault/domain/entities.py` (Zero framework dependencies)
- [x] T006 [P] Implement SQLAlchemy 2.0 persistence models in `modules/gateway/models/` (`project.py`, `service.py`, `client.py`, `virtual_key.py`, `quota.py`, `audit.py`)
- [x] T007 [P] Implement SQLAlchemy 2.0 persistence models in `modules/vault/models/` (`scope.py`, `secret.py`)
- [x] T008 Register gateway and vault models in `migrations/env.py`
- [x] T009 Update `tests/test_clean_architecture_purity.py` to assert zero framework dependencies for gateway and vault domain entities

**Checkpoint**: Foundation domain and models in place, verified by passing purity tests.

---

## Phase 2: Foundational (Database Migration & Gateway Engine Check)

**Purpose**: Database schema creation and live container verification.

- [x] T010 Create and apply Alembic migration for Phase 0 tables (`projects`, `upstream_services`, `registered_clients`, `virtual_access_keys`, `quota_policies`, `audit_events`, `secret_scopes`, `secrets`, `secret_histories`) in `migrations/versions/002_gateway_and_vault.py`
- [x] T011 Verify Docker Compose startup and APISIX Admin API responsiveness (`curl http://localhost:9180/apisix/admin/routes`)

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Client Identity & Key Binding Enforcement at API Gateway (Priority: P1) 🎯 MVP

**Goal**: Every Registered Client (`User Device` or `App Server`) can only call upstream APIs when presenting valid mTLS credentials and its bound `Virtual Access Key`. Stolen/copied keys are rejected with HTTP 403.

**Independent Test**: Simulate two clients (Client A and Client B). Client A calls upstream successfully. Client B presents Client A's key and receives immediate HTTP 403 Forbidden.

### Implementation for User Story 1

- [x] T012 [P] [US1] Implement Private CA and x509 client certificate generation in `core/security/ca.py`
- [x] T013 [P] [US1] Implement Gateway repositories and Dishka provider in `modules/gateway/repository/` and `modules/gateway/di.py`
- [x] T014 [US1] Implement Use Case `RegisterClientUseCase` and `GenerateVirtualKeyUseCase` in `modules/gateway/use_cases/`
- [x] T015 [US1] Implement APISIX Admin API client in `modules/gateway/client/apisix_client.py` to sync consumers and keys
- [x] T016 [US1] Develop APISIX custom Lua plugin `apps/apisix/plugins/identity-binding-filter.lua` verifying `$ssl_client_fingerprint` against Redis cached key ownership
- [x] T017 [US1] Create FastAPI endpoints in `apps/api/routers/gateway.py` for client registration and key issuance
- [x] T018 [US1] Add integration test in `tests/integration/test_identity_binding.py` verifying mTLS + Virtual Key match, and 403 on mismatch

**Checkpoint**: User Story 1 is functional and testable independently.

---

## Phase 4: User Story 2 - Role-Based Centralized Secret Management without Plaintext Files (Priority: P2)

**Goal**: Centralize configuration secrets in PostgreSQL encrypted with AES-256-GCM. Deliver secrets dynamically based on DUT AI SSO role (e.g. Financial vs General). Zero `.env` files on disk.

**Independent Test**: Authenticate as a Financial Developer and a General Developer. Financial receives payment keys + common keys; General receives only common keys and is rejected for financial scopes.

### Implementation for User Story 2

- [x] T019 [P] [US2] Implement AES-256-GCM authenticated encryption service in `modules/vault/services/encryption.py`
- [x] T020 [P] [US2] Implement Vault repository and Dishka provider in `modules/vault/repository/` and `modules/vault/di.py`
- [x] T021 [US2] Implement Use Cases `CreateSecretUseCase` and `GetSecretsByScopeUseCase` enforcing RBAC based on DUT AI SSO role in `modules/vault/use_cases/`
- [x] T022 [US2] Create FastAPI endpoints in `apps/api/routers/vault.py` (`POST /api/v1/vault/projects/{id}/secrets`, `GET /api/v1/vault/projects/{id}/secrets`)
- [x] T023 [US2] Add integration test in `tests/integration/test_vault_rbac.py` verifying role scoping (Financial vs General) and zero plaintext in DB

**Checkpoint**: User Stories 1 AND 2 are both functional and testable.

---

## Phase 5: User Story 3 - Real-Time In-Memory SDK Secret Hot-Reloading (Priority: P3)

**Goal**: When secrets change on the Control Plane, running application processes update their in-memory configurations in < 5 seconds without restarting and without writing files to disk.

**Independent Test**: Run a client process with SDK. Update a secret on Control Plane. Verify the running process reflects the updated value in RAM within 5 seconds.

### Implementation for User Story 3

- [ ] T024 [P] [US3] Implement Redis Pub/Sub publisher for secret modification events in `modules/vault/services/broadcaster.py`
- [ ] T025 [US3] Implement SSE endpoint `GET /api/v1/vault/projects/{id}/stream` using `sse-starlette` in `apps/api/routers/vault.py`
- [ ] T026 [US3] Develop lightweight client CLI/SDK in `packages/dut-vault-sdk/` with in-memory injection (`os.environ` drop-in runner) and SSE live-reload listener
- [ ] T027 [US3] Add integration test in `tests/integration/test_vault_hot_reload.py` verifying memory update in < 5s with zero disk writes

**Checkpoint**: User Stories 1, 2, and 3 work together end-to-end.

---

## Phase 6: User Story 4 - Service Scoping Allowlist & Atomic Quota Enforcement (Priority: P4)

**Goal**: Enforce project-level service allowlists and atomic rate limits (RPM/daily) on APISIX.

**Independent Test**: Project A calls Service Z (unauthorized) -> 403 Forbidden. Project A exceeds 10 RPM to Service X -> 429 Too Many Requests.

### Implementation for User Story 4

- [ ] T028 [P] [US4] Implement Upstream Service management and project allowlist verification in `modules/gateway/use_cases/sync_service.py`
- [ ] T029 [US4] Configure APISIX `proxy-rewrite` plugin to inject real upstream credentials and strip virtual keys
- [ ] T030 [US4] Configure APISIX `limit-count` plugin backed by Redis for atomic RPM/daily quota enforcement
- [ ] T031 [US4] Add integration test in `tests/integration/test_quota_scoping.py` verifying HTTP 403 on unpermitted services and HTTP 429 on quota exhaustion

**Checkpoint**: All 4 user stories are functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Dashboard UI, immutable audit logging, and final validation.

- [ ] T032 [P] Build Next.js Web UI for Secrets Management in `web/src/features/vault/`
- [ ] T033 [P] Build Next.js Web UI for Gateway Projects, Services, and Quota in `web/src/features/gateway/`
- [ ] T034 Implement immutable audit logging writer in `modules/gateway/services/audit.py`
- [ ] T035 Execute end-to-end quickstart validation scenarios from `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Completed! [T001 - T009].
- **Phase 2 (Foundational)**: Unlocks User Story implementation.
- **Phase 3 (User Story 1 - P1)**: Core Zero-Trust Gateway MVP.
- **Phase 4 (User Story 2 - P2)**: Centralized Secrets & RBAC.
- **Phase 5 (User Story 3 - P3)**: In-Memory Hot-Reload SDK.
- **Phase 6 (User Story 4 - P4)**: Service Scoping & Quota.
- **Phase 7 (Polish)**: Web UI and Audit hardening.
