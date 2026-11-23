# Implementation Plan: Gateway Real-Time Quota & Rate Limiting Enforcement (Phase 2)

**Branch**: `014-gateway-quota-rate-limiting` | **Date**: 2026-11-23 | **Spec**: [specs/014-gateway-quota-rate-limiting/spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/014-gateway-quota-rate-limiting/spec.md)

**Input**: Feature specification from `specs/014-gateway-quota-rate-limiting/spec.md`

## Summary
Implement live traffic shaping and daily consumption control across the API Gateway infrastructure:
1. Inject Apache APISIX `limit-count` plugin into upstream service routes to enforce per-Virtual-Key requests-per-minute (`rate_limit_rpm`), returning `HTTP 429 Too Many Requests` at ingress.
2. Integrate Redis atomic counters (`INCR`) in `VerifyIdentityBindingUseCase` to track daily request volume per `(project_id, service_id)` pair, rejecting requests once `quota_daily` is reached.
3. Expose usage metrics via `GET /api/v1/gateway/projects/{id}/services/{id}/usage` and enrich `ProjectAllowedServiceResponse`.
4. Update Frontend `allowed-services-table.tsx` with visual progress bars and warning states.

## Technical Context
- **Language/Version**: Python 3.12 (Backend), TypeScript 5.6 (Frontend), Lua 5.1 (APISIX OpenResty).
- **Primary Dependencies**: FastAPI, Dishka, SQLAlchemy (asyncpg), redis.asyncio, Apache APISIX 3.9, Next.js 16, Tailwind CSS v4.
- **Storage**: PostgreSQL (`quota_policies`), Redis (`gateway:quota:{project_id}:{service_id}:{YYYYMMDD}` with 48h TTL).
- **Testing**: `pytest`, `httpx` for live E2E gateway verification.
- **Target Platform**: Docker containerized APISIX + FastAPI backend + Next.js web application.

## Constitution Check
- **I. Clean Architecture**: Quota domain calculations remain in Domain entities; Redis persistence calls abstracted via `IQuotaUsageStore` or application service. (PASS)
- **II. Modular Monolith**: Dishka DI injects Redis client / quota service into `VerifyIdentityBindingUseCase`. (PASS)
- **III. Transactional Outbox**: Quota counters are in-memory volatile counters in Redis; outbox events emitted only for security/audit alerts. (PASS)
- **IV. Offline Contracts**: OpenAPI schemas updated and types synced via `make api-types`. (PASS)
- **VIII. Gateway Enforcement**: APISIX `limit-count` and `identity-binding-filter` enforce protection directly at ingress. (PASS)

## Project Structure

### Documentation (this feature)
```text
specs/014-gateway-quota-rate-limiting/
├── plan.md              # This file
├── research.md          # Architectural decisions & research
├── data-model.md        # Entities, Redis schemas & DTOs
├── quickstart.md        # Runnable verification guide
├── contracts/           # API endpoints & contracts
│   └── quota-enforcement-api.md
└── tasks.md             # Tasks definition (Phase 2 output)
```

## Architecture & Implementation Steps

### Phase 1: APISIX `limit-count` Rate Limiting Configuration
1. Update `modules/gateway/client/apisix_client.py` in `sync_upstream_service_route()`:
   - Add `limit-count` plugin to plugins dictionary:
     ```python
     plugins["limit-count"] = {
         "count": rate_limit_rpm,
         "time_window": 60,
         "rejected_code": 429,
         "key_type": "var",
         "key": "http_x_virtual_key",
     }
     ```
   - Update `proxy-rewrite` headers to remove `X-Virtual-Key` and `X-Project-Id` before forwarding to upstream.
2. In `apps/apisix/plugins/identity-binding-filter.lua`:
   - Keep `X-Virtual-Key` intact in `rewrite` phase so `limit-count` can read it, letting `proxy-rewrite` strip it at proxy time.

### Phase 2: Redis Daily Quota Tracking (Control Plane)
1. Define `IQuotaUsageTracker` interface in `modules/gateway/domain/interfaces.py`:
   - `get_usage(project_id: str, service_id: str) -> int`
   - `increment_and_check(project_id: str, service_id: str, quota_daily: int) -> tuple[int, bool]`
2. Implement `RedisQuotaUsageTracker` in `modules/gateway/repository/redis_quota_tracker.py` using `redis_settings.get_async_client()`.
3. Register `RedisQuotaUsageTracker` in Dishka DI (`modules/gateway/di.py`).
4. Update `VerifyIdentityBindingUseCase` in `modules/gateway/use_cases/verify_identity_binding.py`:
   - If `service_slug` / `service_id` is present, look up the `QuotaPolicyEntity` for the project & service.
   - Increment Redis counter. If exceeded, raise `DailyQuotaExceededError`.

### Phase 3: Quota Usage Inspection API
1. Implement `GetProjectServiceUsageUseCase` in `modules/gateway/use_cases/get_project_service_usage.py`.
2. Add endpoint `GET /api/v1/gateway/projects/{project_id}/services/{service_id}/usage` in `apps/api/routers/gateway_router.py`.
3. Enrich `GET /api/v1/gateway/projects/{project_id}/services` to include `usage_today` and `usage_percentage`.

### Phase 4: Frontend UI Enhancement
1. Run `make api-types` to refresh TypeScript types.
2. Update `web/src/features/projects/components/allowed-services-table.tsx`:
   - Render a quota progress bar in each service row.
   - Format: `{usage_today.toLocaleString()} / {quota_daily.toLocaleString()} ({usage_percentage}%)`.
   - Apply color styles: green (<80%), yellow (80-99%), red (≥100%).

### Phase 5: Verification & Testing
1. Integration test: `tests/integration/test_gateway_quota_enforcement.py`.
2. Live E2E test in `tests/integration/test_gateway_live_e2e.py` verifying rate limiting 429 and daily quota 429.
