# Implementation Plan: Audit Logging & Security Alerts System (Phase 3)

**Branch**: `015-audit-logging-security-alerts` | **Date**: 2026-11-23 | **Spec**: [specs/015-audit-logging-security-alerts/spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/015-audit-logging-security-alerts/spec.md)

**Input**: Feature specification from `specs/015-audit-logging-security-alerts/spec.md`

## Summary
Implement an immutable security audit logging service and real-time security anomaly alert system fulfilling FR-12 and FR-03:
1. Define `IAuditEventRepository` interface in `modules/gateway/domain/interfaces.py` and implement `SqlAuditEventRepository` in `modules/gateway/repository/audit_repository.py` backed by the existing `audit_events` PostgreSQL table.
2. Integrate automatic event recording in `VerifyIdentityBindingUseCase` to log `ALLOW` events on valid gateway traffic and `DENY` events with exact error codes (`IDENTITY_MISMATCH`, `DAILY_QUOTA_EXCEEDED`, `CLIENT_REVOKED`, `INVALID_KEY`, `SERVICE_NOT_ALLOWED`).
3. Build backend use cases `ListAuditEventsUseCase` and `GetSecurityAlertsUseCase` with REST endpoints `GET /api/v1/gateway/audit-events` and `GET /api/v1/gateway/security-alerts` in `apps/api/routers/gateway_router.py`.
4. Add "Nhật ký an ninh" navigation to Web UI sidebar (`web/src/components/layout/app-shell.tsx`) and build the `/audit` page with `AuditLogsTable`, `AuditFiltersBar`, and `SecurityAlertBanner`.
5. Create comprehensive automated integration tests and verify against live APISIX traffic.

## Technical Context
- **Language/Version**: Python 3.12 (Backend), TypeScript 5.6 (Frontend).
- **Primary Dependencies**: FastAPI, Dishka IoC, SQLAlchemy (asyncpg), Next.js 16 (App Router), TanStack React Query, Lucide React, Tailwind CSS v4.
- **Storage**: PostgreSQL (`audit_events` table with indexes on `timestamp`, `actor_id`, `project_id`, `action`).
- **Testing**: `pytest`, `pytest-asyncio`, `httpx`.
- **Target Platform**: Dockerized APISIX + FastAPI backend + Next.js web application.

## Constitution Check
- **I. Clean Architecture & Domain Purity**: `AuditEventEntity` is a pure Python dataclass in `modules/gateway/domain/entities.py`. Business logic for security alert evaluation resides in domain/use case layers, and persistence is accessed via `IAuditEventRepository`. (PASS)
- **II. Modular Monolith with Dishka IoC**: `SqlAuditEventRepository`, `ListAuditEventsUseCase`, and `GetSecurityAlertsUseCase` are registered in `modules/gateway/di.py` with explicit Dishka scopes (`Scope.REQUEST`). (PASS)
- **III. Transactional Outbox Pattern**: Real-time audit logs are persisted synchronously via `SqlAuditEventRepository` for immediate auditability and security compliance. Heavy notifications or external webhooks (if added later) route through outbox. (PASS)
- **IV. Offline Contract & Type Synchronization**: Pydantic schemas in `modules/gateway/dtos/audit_dtos.py` generate TypeScript types via `make api-types` without requiring running backend servers. (PASS)
- **V. Standardized DUT-AI SSO & Identity**: Audit query endpoints enforce authenticated SSO user sessions. User actions record integer user IDs or client string ULIDs appropriately. (PASS)
- **VIII. Gateway Enforcement**: Gateway security decisions from `VerifyIdentityBindingUseCase` are recorded automatically without breaking or slowing down APISIX reverse proxy routing. (PASS)

## Project Structure

### Documentation (this feature)
```text
specs/015-audit-logging-security-alerts/
├── spec.md              # Feature specification
├── plan.md              # This implementation plan
├── research.md          # Architectural decisions & research
├── data-model.md        # Entities, database models & DTOs
├── quickstart.md        # Runnable verification guide
├── contracts/           # API schemas & endpoints
│   └── audit-api.md
└── tasks.md             # Tasks definition (speckit-tasks output)
```

## Architecture & Implementation Steps

### Phase 1: Domain & Repository Layer (Task 3.1 - Part 1)
1. **Domain Interface**:
   - Add `IAuditEventRepository` to `modules/gateway/domain/interfaces.py`:
     - `record_event(event: AuditEventEntity) -> AuditEventEntity`
     - `list_events(...) -> tuple[list[AuditEventEntity], int]`
     - `get_security_alerts(window_minutes: int, threshold: int) -> list[SecurityAlertEntity]`
2. **SQLAlchemy Repository**:
   - Create `modules/gateway/repository/audit_repository.py` (`SqlAuditEventRepository`):
     - Insert `AuditEventModel` from `AuditEventEntity`.
     - Query with dynamic filters (`project_id`, `client_type`, `decision`, `action`, `error_code`, `date_from`, `date_to`) and pagination (`limit`, `offset`).
     - Aggregation query to detect repeated `IDENTITY_MISMATCH` events (count >= 3 within 5 minutes).
3. **Dependency Injection**:
   - Register `SqlAuditEventRepository` as provider for `IAuditEventRepository` in `modules/gateway/di.py`.

### Phase 2: Automatic Audit Recording in Gateway Verification (Task 3.1 - Part 2)
1. **Update `VerifyIdentityBindingUseCase`** (`modules/gateway/use_cases/verify_identity_binding.py`):
   - Inject `IAuditEventRepository`.
   - On successful verification:
     - Record `action="GATEWAY_ACCESS"`, `decision="ALLOW"`, `client_type=client.client_type.value`, `actor_id=client.id`, `project_id=key.project_id`, `service_id=service.id`.
   - On exceptions/denials:
     - In `except` blocks or before raising `IdentityMismatchError`, `DailyQuotaExceededError`, `VirtualAccessKeyRevokedError`, `ServiceNotAllowedError`, or `VirtualAccessKeyNotFoundError`:
     - Record `action="GATEWAY_ACCESS"`, `decision="DENY"`, with `error_code`, `actor_id`, `project_id`, and `client_ip`.
   - Ensure audit recording is wrapped safely so DB logging errors don't cause unhandled 500s.

### Phase 3: Audit Logs & Security Alerts API (Task 3.2)
1. **DTOs**:
   - Create `modules/gateway/dtos/audit_dtos.py` with `AuditEventResponse`, `AuditEventListResponse`, `SecurityAlertItemResponse`, `SecurityAlertsResponse`.
2. **Use Cases**:
   - Create `modules/gateway/use_cases/list_audit_events.py` (`ListAuditEventsUseCase`).
   - Create `modules/gateway/use_cases/get_security_alerts.py` (`GetSecurityAlertsUseCase`).
   - Register both in `modules/gateway/di.py`.
3. **Endpoints in `apps/api/routers/gateway_router.py`**:
   - `GET /api/v1/gateway/audit-events`: Supports filtering and pagination.
   - `GET /api/v1/gateway/security-alerts`: Returns active security anomalies.

### Phase 4: Frontend Web UI (Task 3.3)
1. **Run Contract Generator**:
   - Execute `make api-types` to generate updated TypeScript interfaces.
2. **Navigation**:
   - Update `web/src/components/layout/app-shell.tsx` to add "Nhật ký an ninh" (`/audit`, icon `ShieldAlert`).
3. **Audit Feature Module (`web/src/features/audit/`)**:
   - `services/audit-service.ts`: API client functions.
   - `hooks/use-audit-queries.ts`: TanStack Query hooks.
   - `components/audit-logs-table.tsx`: Clean data table with actor badges (`User Device` blue, `App Server` purple), decision badges (`ALLOW` emerald, `DENY` rose), error badges, and JSON metadata viewer dialog.
   - `components/audit-filters-bar.tsx`: Interactive filter bar.
   - `components/security-alerts-banner.tsx`: Visual alert card for active security anomalies.
4. **Page Component**:
   - Create `web/src/app/(protected)/audit/page.tsx` integrating the table, filters, and alert banner.

### Phase 5: Verification & Quality Gates
1. **Integration Tests**:
   - Create `tests/integration/test_audit_logging_and_alerts.py`:
     - Verify `VerifyIdentityBindingUseCase` records both ALLOW and DENY events.
     - Verify `GET /api/v1/gateway/audit-events` filtering and pagination.
     - Verify `GET /api/v1/gateway/security-alerts` anomaly threshold trigger.
2. **Full Quality Checks**:
   - `uv run ruff check . && uv run ruff format --check .`
   - `uv run pytest tests/`
   - `make test-e2e` (live APISIX mTLS verification)
   - `pnpm tsc --noEmit`
