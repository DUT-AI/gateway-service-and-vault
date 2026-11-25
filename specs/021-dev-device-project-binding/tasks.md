---

description: "Task list for Regular Dev Device Self-Registration & Project Developer Key Binding"
---

# Tasks: Regular Dev Device Self-Registration & Project Developer Key Binding

**Input**: Design documents from `specs/021-dev-device-project-binding/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/device-project-binding-api.md`

**Organization**: Tasks are grouped by user story, adhering to Constitution v2.4.0.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Foundational Repository & Use Case Extensions

- [x] T001 [P] Add `list_by_owner_ids(owner_ids: list[str])` to `IRegisteredClientRepository` in `modules/gateway/domain/interfaces.py` and implement in `modules/gateway/repository/registered_client_repository.py`
- [x] T002 [P] Create `ListProjectAvailableClientsUseCase` in `modules/gateway/use_cases/list_project_available_clients.py`, export in `modules/gateway/use_cases/__init__.py`, and register in `modules/gateway/di.py`
- [x] T003 [P] Update `ListVirtualKeysUseCase.execute(project_id, owner_id_filter=None)` in `modules/gateway/use_cases/list_virtual_keys.py` to support filtering keys by client owner

---

## Phase 2: User Story 1 - Regular Developer Self-Registers Personal mTLS Device (Priority: P1) 🎯 MVP

- [x] T004 [US1] Update `apps/api/routers/gateway/clients.py` to allow `RoleTier.OTHER` on `GET /clients`, `POST /clients` (restricting `RoleTier.OTHER` to `USER_DEVICE` only; `APP_SERVER` returns `403 Forbidden`), and `POST /clients/{id}/revoke` (own devices only)
- [x] T005 [P] [US1] Update `web/src/components/layout/app-shell.tsx` to show "Thiết bị & Client" (`/clients`) in sidebar for `isOtherRole`
- [x] T006 [P] [US1] Update `web/src/features/clients/components/register-client-dialog.tsx` to lock/hide `APP_SERVER` option when `isOtherRole` is true

---

## Phase 3: User Story 2 - Project Developer Binds Developer Devices to Assigned Projects (Priority: P2)

- [x] T007 [US2] Add `GET /api/v1/gateway/projects/{project_id}/available-clients` in `apps/api/routers/gateway/keys.py` protected by `require_role_tier(RoleTier.ADMIN, RoleTier.PROJECT_DEVELOPER)` + `ensure_project_access`
- [x] T008 [P] [US2] Add `listProjectAvailableClients` in `web/src/features/keys/services/keys-service.ts` and `useProjectAvailableClientsQuery` in `web/src/features/keys/hooks/use-keys-queries.ts`
- [x] T009 [US2] Update `web/src/features/keys/components/generate-key-modal.tsx` to fetch project available clients and render owner name/email/avatar alongside each device

---

## Phase 4: User Story 3 - Admin Governance & Regular Dev Read-Only Key Visibility (Priority: P3)

- [x] T010 [US3] Update `GET /api/v1/gateway/projects/{project_id}/keys` in `apps/api/routers/gateway/keys.py` to allow any assigned project member (`get_current_user_context` + `ensure_project_access`), passing `owner_id_filter=str(user_ctx.user_id)` when `user_ctx.is_other`
- [x] T011 [P] [US3] Update `web/src/features/projects/components/project-workspace-tabs.tsx` to show the **Virtual Keys** tab for `isOtherRole`
- [x] T012 [P] [US3] Update `web/src/features/keys/components/virtual-keys-view.tsx` to render in read-only mode (hide "Cấp Virtual Key mới" and "Thu hồi" buttons) when `isOtherRole`

---

## Phase 5: Verification, Type Sync & Quality Gates

- [x] T013 [P] Run `make api-types` and `cd web && pnpm typecheck`
- [x] T014 Write integration test suite `tests/integration/test_dev_device_project_binding.py` covering Tier 3 self-registration (`USER_DEVICE` allowed, `APP_SERVER` 403), Project Developer binding member devices, and Tier 3 read-only Virtual Keys
- [x] T015 Run `uv run ruff check --fix && uv run ruff format` and `uv run pytest`
