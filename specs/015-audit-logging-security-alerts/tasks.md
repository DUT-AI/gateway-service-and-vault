# Tasks: Audit Logging & Security Alerts System (Phase 3)

**Input**: Design documents from `/specs/015-audit-logging-security-alerts/`  
**Prerequisites**: [plan.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/015-audit-logging-security-alerts/plan.md), [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/015-audit-logging-security-alerts/spec.md), [research.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/015-audit-logging-security-alerts/research.md), [data-model.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/015-audit-logging-security-alerts/data-model.md), [contracts/audit-api.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/015-audit-logging-security-alerts/contracts/audit-api.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are explicitly provided for all tasks

---

## Phase 1: Foundational (Core Repository & Interface)

**Purpose**: Core domain and persistence contracts required by all user stories

- [X] T001 [P] Define `SecurityAlertEntity` dataclass with `alert_id: str`, `severity: str`, `anomaly_type: str`, `description: str`, `actor_id: str | None`, `client_ip: str | None`, `event_count: int`, `first_seen_at: datetime`, `last_seen_at: datetime` in `modules/gateway/domain/entities.py`
- [X] T002 [P] Define `IAuditEventRepository` abstract interface with `record_event(event: AuditEventEntity)`, `list_events(...)`, and `get_security_alerts(...)` in `modules/gateway/domain/interfaces.py`
- [X] T003 Implement `SqlAuditEventRepository` in `modules/gateway/repository/audit_repository.py` using `AuditEventModel` for persistence, dynamic query filtering, and repeated mismatch aggregation
- [X] T004 Register `SqlAuditEventRepository` as provider for `IAuditEventRepository` (scope `Scope.REQUEST`) in `modules/gateway/di.py`

**Checkpoint**: Repository and domain interfaces ready for event recording and querying.

---

## Phase 2: User Story 1 - Immutable Audit Logging for Gateway Access Decisions (Priority: P1) 🎯 MVP

**Goal**: Automatically record every gateway verification decision (`ALLOW` or `DENY`) with actor type, error code, and metadata in PostgreSQL without impacting request processing.

**Independent Test**: Call `VerifyIdentityBindingUseCase` with valid credentials and invalid/mismatched credentials; inspect database to ensure matching `ALLOW` and `DENY` records are persisted with exact fields.

### Tests for User Story 1
- [X] T005 [P] [US1] Create integration test `tests/integration/test_audit_event_recorder.py` testing persistence of `ALLOW` events and `DENY` events (`IDENTITY_MISMATCH`, `DAILY_QUOTA_EXCEEDED`, `CLIENT_REVOKED`)

### Implementation for User Story 1
- [X] T006 [US1] Inject `IAuditEventRepository` into `VerifyIdentityBindingUseCase.__init__` in `modules/gateway/use_cases/verify_identity_binding.py`
- [X] T007 [US1] Record `ALLOW` audit event on successful identity binding and quota check in `VerifyIdentityBindingUseCase.execute` in `modules/gateway/use_cases/verify_identity_binding.py`
- [X] T008 [US1] Record `DENY` audit events on `IdentityMismatchError`, `DailyQuotaExceededError`, `VirtualAccessKeyRevokedError`, and missing/invalid keys in `VerifyIdentityBindingUseCase.execute` in `modules/gateway/use_cases/verify_identity_binding.py`
- [X] T009 [US1] Run `pytest tests/integration/test_audit_event_recorder.py` and verify all tests pass

**Checkpoint**: User Story 1 fully functional and testable independently.

---

## Phase 3: User Story 2 - Audit Log Query & Security Anomaly Detection API (Priority: P2)

**Goal**: Provide REST endpoints `GET /api/v1/gateway/audit-events` (filtering, pagination) and `GET /api/v1/gateway/security-alerts` (anomalies detection).

**Independent Test**: Call the endpoints with query parameters (`project_id`, `client_type`, `decision`, `error_code`, `limit`, `offset`) and verify accurate filtered results and detection of repeated mismatches.

### Implementation for User Story 2
- [X] T010 [P] [US2] Create DTOs `AuditEventResponse`, `AuditEventListResponse`, `SecurityAlertItemResponse`, `SecurityAlertsResponse` in `modules/gateway/dtos/audit_dtos.py`
- [X] T011 [P] [US2] Implement `ListAuditEventsUseCase` in `modules/gateway/use_cases/list_audit_events.py` supporting filters and pagination
- [X] T012 [P] [US2] Implement `GetSecurityAlertsUseCase` in `modules/gateway/use_cases/get_security_alerts.py` to retrieve active security anomalies
- [X] T013 [US2] Export new use cases in `modules/gateway/use_cases/__init__.py` and bind them in `modules/gateway/di.py` with `Scope.REQUEST`
- [X] T014 [US2] Add endpoints `GET /api/v1/gateway/audit-events` and `GET /api/v1/gateway/security-alerts` with query parameters in `apps/api/routers/gateway_router.py`
- [X] T015 [US2] Create integration test `tests/integration/test_audit_api_and_alerts.py` verifying query filters, pagination, and anomaly alert detection

**Checkpoint**: User Story 2 complete; REST APIs ready and covered by integration tests.

---

## Phase 4: User Story 3 - Web UI "Nhật Ký An Ninh & Cảnh Báo" (Priority: P2)

**Goal**: Deliver a dedicated UI view (`/audit`) with a high-visibility security alert banner, comprehensive filter bar, and audit logs table.

**Independent Test**: Navigate to `http://localhost:3000/audit`, verify sidebar link works, test filtering by `DENY`, and inspect actor badges and metadata modal.

### Implementation for User Story 3
- [X] T016 [US3] Run `make api-types` to regenerate TypeScript types from backend Pydantic schemas in `web/src/types/api.generated.d.ts`
- [X] T017 [P] [US3] Create API client `auditService` in `web/src/features/audit/services/audit-service.ts` for fetching audit events and security alerts
- [X] T018 [P] [US3] Create React Query hooks `useAuditEventsQuery` and `useSecurityAlertsQuery` in `web/src/features/audit/hooks/use-audit-queries.ts`
- [X] T019 [P] [US3] Implement `SecurityAlertsBanner` in `web/src/features/audit/components/security-alerts-banner.tsx` displaying alert descriptions, event counts, and timestamps
- [X] T020 [P] [US3] Implement `AuditFiltersBar` in `web/src/features/audit/components/audit-filters-bar.tsx` with decision, client type, project, and error code selectors
- [X] T021 [US3] Implement `AuditLogsTable` in `web/src/features/audit/components/audit-logs-table.tsx` with actor type badges (`USER_DEVICE` vs `APP_SERVER`), decision badges (`ALLOW` emerald vs `DENY` rose), error codes, and metadata JSON dialog
- [X] T022 [US3] Add "Nhật ký an ninh" navigation item with `ShieldAlert` icon to `NAV_ITEMS` in `web/src/components/layout/app-shell.tsx`
- [X] T023 [US3] Create page `web/src/app/(protected)/audit/page.tsx` composing `SecurityAlertsBanner`, `AuditFiltersBar`, and `AuditLogsTable`

**Checkpoint**: User Story 3 complete; Web UI is fully functional and responsive.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verification, documentation, and quality gates across all layers

- [X] T024 [P] Update `docs/CHECKLIST_REMAINING_TASKS.md` marking Phase 3 tasks as completed
- [X] T025 Run code formatting and linting: `uv run ruff check .` and `uv run ruff format --check .`
- [X] T026 Run backend test suite: `uv run pytest tests/` (all unit and integration tests)
- [X] T027 Run frontend type check: `pnpm --filter web typecheck` or `pnpm tsc --noEmit`
- [X] T028 Run live APISIX automated E2E tests: `make test-e2e` to ensure zero regression in gateway verification

---

## Dependencies & Execution Order

### Phase Dependencies
- **Foundational (Phase 1)**: No dependencies - can start immediately
- **User Story 1 (Phase 2)**: Depends on Phase 1 completion
- **User Story 2 (Phase 3)**: Depends on Phase 1 completion (can build in parallel with US1)
- **User Story 3 (Phase 4)**: Depends on Phase 3 (needs API contracts from US2)
- **Polish (Phase 5)**: Depends on all user stories (US1, US2, US3) being implemented

### User Story Dependencies
- **US1 (P1)**: Independent backend recording (MVP)
- **US2 (P2)**: Uses `IAuditEventRepository` from Phase 1 to expose query & alerts API
- **US3 (P2)**: Uses API from US2 to render Web UI dashboard

### Parallel Opportunities
- In Phase 1: `T001` and `T002` can run in parallel.
- In Phase 3: `T010`, `T011`, and `T012` can be authored in parallel.
- In Phase 4: `T017`, `T018`, `T019`, and `T020` can be built in parallel.

---

## Implementation Strategy

### MVP First (User Story 1)
1. Complete Phase 1: Repository & Domain contracts.
2. Complete Phase 2: User Story 1 (automatic recording in `VerifyIdentityBindingUseCase`).
3. Verify with `test_audit_event_recorder.py`. This delivers immediate compliance and logging at the Gateway.

### Incremental Delivery (API & UI)
4. Complete Phase 3: Expose `GET /api/v1/gateway/audit-events` and `GET /api/v1/gateway/security-alerts`.
5. Complete Phase 4: Build `/audit` UI page and navigation.
6. Complete Phase 5: Run full test suite, linting, and live mTLS E2E tests.
