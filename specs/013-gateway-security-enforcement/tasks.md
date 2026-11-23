# Tasks: Core Security & Gateway Enforcement (Phase 1)

**Input**: Design documents from `specs/013-gateway-security-enforcement/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Organization
Tasks are strictly organized by user story and implementation phase to enable independent implementation, testing, and progressive verification.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Associated user story (US1, US2, US3, US4)

---

## Phase 1: Setup & APISIX Infrastructure Configuration

**Purpose**: Prepare APISIX container and plugin directory mounting so the custom Lua filter can be executed at runtime.

- [x] T001 [Setup] Mount `./apps/apisix/plugins:/usr/local/apisix/plugins:ro` in `docker-compose.yml` under `apisix` service
- [x] T002 [Setup] Configure `apps/apisix/conf/config.yaml` to set `extra_lua_path: "/usr/local/apisix/plugins/?.lua"` and declare `identity-binding-filter` in the plugins list
- [x] T003 [Setup] Restart APISIX container (`docker compose restart apisix`) and verify clean initialization via container logs

---

## Phase 2: Foundational (Backend Contract & DTOs)

**Purpose**: Core DTOs and repository interfaces required before user stories can be implemented.

- [x] T004 [P] [Foundation] Add `service_slug: str | None = None` to `VerifyBindingRequest` in `modules/gateway/dtos/gateway_dtos.py`
- [x] T005 [P] [Foundation] Add `RevokeClientResponse` DTO to `modules/gateway/dtos/gateway_dtos.py`
- [x] T006 [Foundation] Define `revoke_client(client_id: str) -> bool` in `IRegisteredClientRepository` in `modules/gateway/domain/interfaces.py`

---

## Phase 3: User Story 1 - APISIX Runtime Identity Binding & mTLS Enforcement (Priority: P1) 🎯 MVP

**Goal**: Enforce mandatory mTLS client certificates and valid `X-Virtual-Key` header on all `/services/*` routes via APISIX Lua filter.

**Independent Test**:
Call `http://localhost:9080/services/llm/models` without `X-Virtual-Key` -> Rejected with `401 Unauthorized`.
Call with `X-Virtual-Key` but without mTLS certificate over HTTP -> Rejected with `403 Forbidden` (`MTLS_REQUIRED`).
Call with valid mTLS certificate and valid virtual key -> Returns `200 OK`.

- [x] T007 [US1] Update `apps/apisix/plugins/identity-binding-filter.lua` to enforce mandatory client certificate (`ngx.var.ssl_client_fingerprint`) and `X-Virtual-Key` header, failing closed if either is missing
- [x] T008 [US1] Update `modules/gateway/client/apisix_client.py` in `sync_upstream_service_route` to inject `identity-binding-filter` into route plugins payload
- [x] T009 [US1] Synchronize APISIX upstream routes on startup and trigger reload for active upstream services
- [x] T010 [US1] Create integration test `tests/integration/test_gateway_security_enforcement.py` verifying that unauthenticated or non-mTLS requests are rejected

---

## Phase 4: User Story 2 - Service Scoping Enforcement at Gateway Ingress (Priority: P1)

**Goal**: Extract `service_slug` in the Lua filter and verify that the calling Project has permission to access the target upstream service.

**Independent Test**:
Call an allowed service for Project A -> Returns `200 OK`.
Call an unallowed service for Project A -> Returns `403 Forbidden` (`ServiceNotPermittedError`).

- [x] T011 [US2] Update `apps/apisix/plugins/identity-binding-filter.lua` to extract `service_slug` from `ngx.var.uri` (`^/services/([^/]+)`) and include it in the verification request body
- [x] T012 [US2] Update `VerifyIdentityBindingUseCase` in `modules/gateway/use_cases/verify_identity_binding.py` to resolve `service_slug` to service entity and verify `is_service_allowed(project_id, service.id)`
- [x] T013 [US2] Update endpoint `POST /api/v1/gateway/verify-binding` in `apps/api/routers/gateway_router.py` to accept and pass `service_slug`
- [x] T014 [US2] Add integration tests in `tests/integration/test_gateway_security_enforcement.py` verifying service scoping allowlist enforcement

---

## Phase 5: User Story 3 - Hardware/Device Identity Revocation (Revoke Client Backend) (Priority: P1)

**Goal**: Enable administrators to revoke a registered client device, atomically invalidating the device record and all associated virtual keys.

**Independent Test**:
Call `POST /api/v1/gateway/clients/{id}/revoke` -> Returns `200 OK`.
Verify `client.is_revoked == True` and all active keys for that client have `status == REVOKED`.
Subsequent requests using credentials from this client return `403 Forbidden`.

- [x] T015 [US3] Implement `revoke_client` in `modules/gateway/repository/gateway_repository.py` using atomic transaction to set `is_revoked = True` and transition all active virtual keys for the client to `REVOKED`
- [x] T016 [US3] Implement `RevokeClientUseCase` in `modules/gateway/use_cases/revoke_client.py`
- [x] T017 [US3] Register `RevokeClientUseCase` in `modules/gateway/di.py` under `Scope.REQUEST`
- [x] T018 [US3] Implement `POST /api/v1/gateway/clients/{client_id}/revoke` endpoint in `apps/api/routers/gateway_router.py`
- [x] T019 [US3] Add integration tests in `tests/integration/test_gateway_security_enforcement.py` verifying client revocation and subsequent request rejection

---

## Phase 6: User Story 4 - Visual Client Revocation on Web UI (Priority: P2)

**Goal**: Provide an intuitive and safe UI in `/clients` allowing administrators to revoke client devices with a confirmation dialog.

**Independent Test**:
Navigate to `/clients` in web browser.
Click "Thu hồi thiết bị" on an active client row -> Confirmation modal appears.
Confirm revocation -> Status badge changes to red `REVOKED`, revocation action is disabled, and success toast displays.

- [x] T020 [US4] Export updated OpenAPI schema and regenerate frontend TypeScript types (`web/src/types/api.generated.d.ts`)
- [x] T021 [US4] Add `revokeClient(id: string)` to `web/src/features/clients/services/client-service.ts`
- [x] T022 [US4] Add `useRevokeClientMutation` in `web/src/features/clients/hooks/use-clients-queries.ts` with cache invalidation for `['registered-clients']` and `['virtual-keys']`
- [x] T023 [US4] Update `web/src/features/clients/components/clients-table.tsx` with "Thu hồi thiết bị" button, confirmation dialog, disabled state, and red `REVOKED` badge

---

## Phase 7: Polish & Verification

**Purpose**: Cross-cutting verification, code quality, and end-to-end execution.

- [x] T024 [Polish] Run entire pytest test suite (`uv run pytest tests/`) and verify all tests pass
- [x] T025 [Polish] Run linter and formatting checks (`uv run ruff check` and `pnpm tsc --noEmit`)
- [x] T026 [Polish] Execute live validation scenarios from `quickstart.md` against APISIX and FastAPI backend
