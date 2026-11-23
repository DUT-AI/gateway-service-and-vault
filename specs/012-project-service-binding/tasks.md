# Tasks: Project Upstream Service Binding & Quota Governance

**Input**: Design documents from `specs/012-project-service-binding/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project schema verification and DTO definitions

- [x] T001 Inspect existing gateway database models in `modules/gateway/models/project.py` and `modules/gateway/models/quota.py`
- [x] T002 [P] Setup DTOs for project service binding and quota policies (`ProjectAllowedServiceResponse`, `BindServiceToProjectRequest`, `UpdateServiceQuotaRequest`) in `modules/gateway/dtos/gateway_dtos.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core repository and IoC infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 [P] Define repository interface methods for service binding and quota management in `modules/gateway/domain/interfaces.py`
- [x] T004 Implement repository persistence methods (`list_allowed_services_with_quota`, `bind_service_to_project`, `unbind_service_from_project`, `update_service_quota`) in `modules/gateway/repository/gateway_repository.py`
- [x] T005 Register new use cases in Dishka IoC container in `modules/gateway/di.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View Allowed Upstream Services for a Project (Priority: P1) 🎯 MVP

**Goal**: Enable project administrators to view all upstream services authorized for their project with current quota limits and active status inside the Project Workspace.

**Independent Test**: Navigate to `/projects/{id}`, click "Dịch vụ liên kết" tab, and verify that bound services and their quotas are displayed in a structured table, or an informative empty state if no services are bound.

### Implementation for User Story 1

- [x] T006 [P] [US1] Create `ListProjectAllowedServicesUseCase` in `modules/gateway/use_cases/list_project_allowed_services.py`
- [x] T007 [US1] Implement `GET /api/v1/gateway/projects/{project_id}/services` route handler in `apps/api/routers/gateway_router.py`
- [x] T008 [P] [US1] Create React Query hooks (`useProjectServicesQuery`) and API client functions in `web/src/features/projects/api/project-services.ts`
- [x] T009 [US1] Implement `AllowedServicesTable` component showing bound services with status, base URLs, and quotas in `web/src/features/projects/components/allowed-services-table.tsx`
- [x] T010 [US1] Integrate "Dịch vụ liên kết" tab into `ProjectWorkspaceTabs` in `web/src/features/projects/components/project-workspace-tabs.tsx`

**Checkpoint**: User Story 1 is functional and can be tested independently.

---

## Phase 4: User Story 2 - Bind Upstream Service to Project with Quota Allocation (Priority: P1)

**Goal**: Allow project administrators to select an upstream service from the catalog, configure rate limit RPM and daily request quota, and bind it to the project.

**Independent Test**: Open the "Thêm dịch vụ" dialog in the project workspace, select an unbound service, specify quota numbers (e.g. 60 RPM, 10,000 requests/day), confirm, and observe the service immediately appearing in the table.

### Implementation for User Story 2

- [x] T011 [P] [US2] Create `BindServiceToProjectUseCase` with duplicate check and validation in `modules/gateway/use_cases/bind_service_to_project.py`
- [x] T012 [US2] Implement `POST /api/v1/gateway/projects/{project_id}/services` endpoint in `apps/api/routers/gateway_router.py`
- [x] T013 [P] [US2] Create `BindServiceDialog` with searchable upstream service select, RPM and Daily Quota inputs in `web/src/features/projects/components/bind-service-dialog.tsx`
- [x] T014 [US2] Add mutation hook `useBindServiceMutation` with query invalidation in `web/src/features/projects/api/project-services.ts` and integrate dialog into `ProjectAllowedServicesView`

**Checkpoint**: User Story 2 is functional and integrates seamlessly with User Story 1.

---

## Phase 5: User Story 3 - Modify Quotas and Revoke Service Access (Priority: P2)

**Goal**: Allow administrators to update quota policies or revoke/unbind access to an upstream service with instant effect.

**Independent Test**: Click "Xóa quyền" on a bound service row, confirm the prompt, and verify the service is removed. Update quota limits on an existing row and verify changes persist.

### Implementation for User Story 3

- [x] T015 [P] [US3] Create `UnbindServiceFromProjectUseCase` in `modules/gateway/use_cases/unbind_service_from_project.py`
- [x] T016 [P] [US3] Create `UpdateProjectServiceQuotaUseCase` in `modules/gateway/use_cases/update_project_service_quota.py`
- [x] T017 [US3] Implement `DELETE /api/v1/gateway/projects/{project_id}/services/{service_id}` and `PUT /api/v1/gateway/projects/{project_id}/services/{service_id}/quota` endpoints in `apps/api/routers/gateway_router.py`
- [x] T018 [P] [US3] Create unbind and quota update mutations in `web/src/features/projects/api/project-services.ts`
- [x] T019 [US3] Add unbind confirmation dialog and quota edit actions in `web/src/features/projects/components/allowed-services-table.tsx`

**Checkpoint**: User Story 3 is complete with full lifecycle management.

---

## Phase 6: User Story 4 - Zero-Trust Gateway Enforcement of Project Allowlist (Priority: P1)

**Goal**: Guarantee that the API Gateway verifies the incoming project virtual key against the project's allowed services allowlist, blocking unauthorized calls with HTTP 403 Forbidden.

**Independent Test**: Execute automated tests asserting that calls to unbound services return HTTP 403 Forbidden while bound services return allowed.

### Implementation for User Story 4

- [x] T020 [P] [US4] Update `VerifyIdentityBindingUseCase` in `modules/gateway/use_cases/verify_identity_binding.py` to enforce project service allowlist check when target service is supplied
- [x] T021 [US4] Add comprehensive unit and integration tests for service binding, quota policy, and gateway enforcement in `tests/test_project_service_binding.py`

**Checkpoint**: Zero-trust security invariant strictly verified.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Offline contract synchronization, type checking, test verification, and code quality

- [x] T022 [P] Regenerate OpenAPI schema and sync TypeScript types via `make api-types`
- [x] T023 [P] Run frontend typecheck `pnpm --prefix web typecheck` and production build `pnpm --prefix web build`
- [x] T024 Run full test suite `uv run pytest tests/test_project_service_binding.py tests/test_gateway_use_cases.py`
- [x] T025 Run linting and code quality checks `uv run ruff check --fix && uv run ruff format`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - starts immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2. Delivers MVP (View Allowed Services).
- **User Story 2 (Phase 4)**: Depends on Phase 2 and US1 DTOs/hooks. Delivers Service Binding.
- **User Story 3 (Phase 5)**: Depends on US1/US2. Delivers Quota Adjustment & Revocation.
- **User Story 4 (Phase 6)**: Depends on Phase 2. Delivers Zero-Trust Gateway Allowlist Enforcement.
- **Polish (Phase 7)**: Depends on all implementation phases.

### Parallel Opportunities

- T002, T003 can run in parallel during Setup/Foundation.
- T006, T008 can run in parallel during US1.
- T011, T013 can run in parallel during US2.
- T015, T016, T018 can run in parallel during US3.
- T020, T022 can run in parallel during Polish/Security.
