# Tasks: Gateway Real-Time Quota & Rate Limiting Enforcement (Phase 2)

**Input**: Design documents from `specs/014-gateway-quota-rate-limiting/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Organization
Tasks are strictly organized by user story and execution phase to enable independent implementation, testing, and progressive verification.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Associated user story (US1, US2, US3, US4)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare and verify APISIX and Redis runtime infrastructure for rate limiting and counters.

- [x] T001 Verify Redis connectivity (`redis_url` on port 6379/6380) in `core/config/redis.py` and ensure `get_async_client()` is operational
- [x] T002 Ensure `limit-count` is enabled in `apps/apisix/conf/config.yaml` plugins list and container reloaded clean

---

## Phase 2: Foundational (Backend Contracts & DTOs)

**Purpose**: Core DTOs, domain interfaces, and exception handlers required before user stories can execute.

- [x] T003 [P] Define `QuotaUsageResponse` DTO in `modules/gateway/dtos/gateway_dtos.py`
- [x] T004 [P] Update `ProjectAllowedServiceResponse` in `modules/gateway/dtos/gateway_dtos.py` with `usage_today: int = 0` and `usage_percentage: float = 0.0`
- [x] T005 [Foundation] Define `IQuotaUsageTracker` interface in `modules/gateway/domain/interfaces.py` with `get_usage` and `increment_and_check` methods
- [x] T006 [Foundation] Define `DailyQuotaExceededError` in `modules/gateway/domain/exceptions.py` and register handler in `core/exceptions/handlers.py` returning HTTP 429

---

## Phase 3: User Story 1 - Live Gateway Rate Limiting per Route via APISIX (Priority: P1) 🎯 MVP

**Goal**: Enforce `rate_limit_rpm` per Virtual Key directly at APISIX ingress using `limit-count` plugin, rejecting burst traffic with `HTTP 429 Too Many Requests`.

**Independent Test**:
Call an upstream route (e.g. `rate_limit_rpm = 5`) 6 times in rapid succession. The 6th call must be rejected immediately at APISIX with `HTTP 429 Too Many Requests` without dispatching to backend.

- [x] T007 [US1] Update `apps/apisix/plugins/identity-binding-filter.lua` to retain `X-Virtual-Key` header during rewrite phase so downstream `limit-count` plugin can read it
- [x] T008 [US1] Update `modules/gateway/client/apisix_client.py` in `sync_upstream_service_route` to inject `limit-count` with `key_type: "var"`, `key: "http_x_virtual_key"`, `time_window: 60`, `count: rate_limit_rpm`, and `rejected_code: 429`
- [x] T009 [US1] Configure `proxy-rewrite` in `modules/gateway/client/apisix_client.py` with `headers: {"remove": ["X-Virtual-Key", "X-Project-Id"]}` before forwarding upstream
- [x] T010 [US1] Resynchronize active upstream routes in APISIX using updated `sync_upstream_service_route`
- [x] T011 [US1] Add integration test in `tests/integration/test_gateway_quota_enforcement.py` verifying APISIX route configuration and `limit-count` plugin payload

---

## Phase 4: User Story 2 - Daily Quota Tracking via Redis Atomic Counter (Priority: P1)

**Goal**: Enforce daily ceiling (`quota_daily`) per `(project_id, service_id)` in `verify-binding` endpoint using atomic Redis `INCR`, returning `429 Too Many Requests` when exhausted.

**Independent Test**:
Configure `quota_daily = 3`. Send 3 requests through `/verify-binding` -> All return 200. Send 4th request -> Returns `429 Too Many Requests` (`Daily request quota exceeded`).

- [x] T012 [US2] Implement `RedisQuotaUsageTracker` in `modules/gateway/repository/redis_quota_tracker.py` using `gateway:quota:{project_id}:{service_id}:{YYYYMMDD}` with 48h TTL and fail-open safety
- [x] T013 [US2] Register `IQuotaUsageTracker` in Dishka DI container (`modules/gateway/di.py`) under `Scope.APP`
- [x] T014 [US2] Update `VerifyIdentityBindingUseCase` in `modules/gateway/use_cases/verify_identity_binding.py` to inject `IQuotaUsageTracker`, look up `quota_daily`, increment counter, and raise `DailyQuotaExceededError` if exceeded
- [x] T015 [US2] Add unit & integration tests in `tests/integration/test_gateway_quota_enforcement.py` verifying atomic increment, date rollover, and 429 error rejection

---

## Phase 5: User Story 3 - Real-Time Quota Usage Inspection API (Priority: P2)

**Goal**: Provide endpoints to query today's consumption for a service and enrich the project's allowed services list.

**Independent Test**:
Call `GET /api/v1/gateway/projects/{project_id}/services/{service_id}/usage` -> Returns `{"usage_today": X, "quota_daily": Y, "usage_percentage": Z}`.
Call `GET /api/v1/gateway/projects/{project_id}/services` -> Each service item contains `usage_today` and `usage_percentage`.

- [x] T016 [US3] Implement `GetProjectServiceUsageUseCase` in `modules/gateway/use_cases/get_project_service_usage.py`
- [x] T017 [US3] Register `GetProjectServiceUsageUseCase` in Dishka DI container (`modules/gateway/di.py`) under `Scope.REQUEST`
- [x] T018 [US3] Implement `GET /api/v1/gateway/projects/{project_id}/services/{service_id}/usage` in `apps/api/routers/gateway_router.py`
- [x] T019 [US3] Update `list_project_services` in `apps/api/routers/gateway_router.py` to query current day usage from `IQuotaUsageTracker` and populate `usage_today` and `usage_percentage`
- [x] T020 [US3] Add integration tests in `tests/integration/test_gateway_quota_enforcement.py` verifying usage calculation and enriched service list response

---

## Phase 6: User Story 4 - Visual Quota Usage Progress Bar on Web UI (Priority: P2)

**Goal**: Display visual progress bars with percentage usage and color-coded warning states on `/projects/{id}` Allowed Services table.

**Independent Test**:
Navigate to `/projects/{id}` in web browser. Observe "Dịch vụ được phép" table showing progress bar with current count, quota ceiling, and color badges.

- [x] T021 [US4] Export updated OpenAPI schema and regenerate frontend TypeScript types (`make api-types`)
- [x] T022 [US4] Update `web/src/features/projects/components/allowed-services-table.tsx` to render a progress bar for daily quota usage with formatted text (`{usage_today} / {quota_daily} requests ({usage_percentage}%)`)
- [x] T023 [US4] Add color styling in `allowed-services-table.tsx`: emerald (<80%), amber (80-99%), rose/red (≥100% with "Hết hạn mức" badge)

---

## Phase 7: Polish & Verification

**Purpose**: Cross-cutting verification, code quality, and end-to-end execution.

- [x] T024 [Polish] Run entire pytest test suite (`uv run pytest tests/`) and verify 100% pass rate
- [x] T025 [Polish] Run linting and static checks (`uv run ruff check`, `uv run ruff format --check`, and `pnpm tsc --noEmit`)
- [x] T026 [Polish] Add live automated E2E tests for rate limiting surge (429) and daily quota ceiling (429) in `tests/integration/test_gateway_live_e2e.py`
