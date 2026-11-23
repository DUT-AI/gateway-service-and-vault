# Tasks: Fail-Closed Hardening & SSO Deactivation Sync (Phase 5)

**Input**: Design documents from `/specs/017-fail-closed-sso-revocation/`  
**Prerequisites**: [plan.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/017-fail-closed-sso-revocation/plan.md), [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/017-fail-closed-sso-revocation/spec.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- File paths are explicitly provided for all tasks

---

## Phase 1: Foundational (Repository Extension)

**Purpose**: Provide client lookup by owner ID required for cascade revocation

- [x] T001 [P] Add `list_by_owner_id(owner_id: str) -> list[RegisteredClientEntity]` to `IRegisteredClientRepository` in `modules/gateway/domain/interfaces.py`
- [x] T002 Implement `list_by_owner_id` in `SqlRegisteredClientRepository` in `modules/gateway/repository/gateway_repository.py`

**Checkpoint**: Repository layer can query all devices owned by an SSO user.

---

## Phase 2: User Story 1 - SSO User Deactivation Sync (Priority: P1) 🎯 MVP

**Goal**: Automatically revoke all devices and active virtual keys when an employee or central account is deactivated on SSO IdP.

**Independent Test**: Register client and keys for user ID `999`; trigger sync-revocation for `999`; verify client is marked revoked, virtual keys are revoked, and subsequent gateway calls fail.

### Tests for User Story 1
- [x] T003 [P] [US1] Create integration test `tests/integration/test_sso_user_revocation_sync.py` testing automatic cascade revocation of clients and virtual keys

### Implementation for User Story 1
- [x] T004 [US1] Implement `SyncSsoUserRevocationUseCase` in `modules/identity/use_cases/sync_sso_user_revocation.py`
- [x] T005 [US1] Register `SyncSsoUserRevocationUseCase` in Dishka DI container in `modules/identity/di.py` and export in `modules/identity/use_cases/__init__.py`
- [x] T006 [US1] Add endpoint `POST /api/v1/identity/users/{user_id}/sync-revocation` in `apps/api/routers/auth_router.py`
- [x] T007 [US1] Run `pytest tests/integration/test_sso_user_revocation_sync.py` and verify all tests pass

**Checkpoint**: User Story 1 complete; SSO revocation sync operational.

---

## Phase 3: User Story 2 - Gateway Fail-Closed Hardening & Verification (Priority: P1)

**Goal**: Harden APISIX Lua filter to strictly fail closed with 403 on timeouts, connection errors, and 5xx responses, ensuring 0 unverified requests reach upstream.

**Independent Test**: Simulate Control Plane timeout and connection failure; verify Gateway returns 403 `CONTROL_PLANE_UNAVAILABLE` and blocks upstream forwarding.

### Implementation for User Story 2
- [x] T008 [P] [US2] Review and harden `apps/apisix/plugins/identity-binding-filter.lua` to return 403 `CONTROL_PLANE_UNAVAILABLE` on network errors, timeouts, and 5xx responses
- [x] T009 [US2] Create integration test `tests/integration/test_fail_closed.py` verifying fail-closed behavior across timeout, unreachable control plane, and invalid keys
- [x] T010 [US2] Run `pytest tests/integration/test_fail_closed.py` and verify 100% pass rate

**Checkpoint**: User Story 2 complete; Gateway fail-closed behavior verified.

---

## Phase 4: Polish & Final Quality Gates

**Purpose**: Cross-cutting validation, documentation, and regression testing

- [x] T011 [P] Update `docs/CHECKLIST_REMAINING_TASKS.md` marking Phase 5 tasks as completed
- [x] T012 Run code formatting and linting: `uv run ruff check .` and `uv run ruff format --check .`
- [x] T013 Run full backend test suite: `uv run pytest tests/` and `make test-e2e`
- [x] T014 Run frontend typecheck: `cd web && pnpm tsc --noEmit`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Foundational)**: Can start immediately.
- **Phase 2 (US1)**: Depends on Phase 1 completion.
- **Phase 3 (US2)**: Can proceed in parallel with Phase 2.
- **Phase 4 (Polish)**: Depends on Phase 2 & 3 completion.

### Parallel Opportunities
- `T001` and `T008` can be authored in parallel.
- `T003` and `T009` can be authored in parallel.
