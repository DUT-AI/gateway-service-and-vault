# Tasks: Developer Onboarding & Docker Machine Experience (Phase 4)

**Input**: Design documents from `/specs/016-developer-onboarding-docker-machine/`  
**Prerequisites**: [plan.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/016-developer-onboarding-docker-machine/plan.md), [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/016-developer-onboarding-docker-machine/spec.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are explicitly provided for all tasks

---

## Phase 1: Foundational & Certificate Bundle Polish (Task 4.1) 🎯 MVP

**Purpose**: Ensure robust, single-click certificate and private key downloads for all registered clients

- [X] T001 [P] [US1] Verify and polish `CertDownloadDialog` in `web/src/features/clients/components/cert-download-dialog.tsx` ensuring `.crt`, `.key`, and combined bundle downloads with copyable fingerprint
- [X] T002 [US1] Export `downloadFile` helper and client dialog components in `web/src/features/clients/index.ts`

**Checkpoint**: User Story 1 complete; certificate bundle downloads verified.

---

## Phase 2: User Story 2 - Docker Machine Workload Guide (Priority: P2)

**Goal**: Provide an interactive dialog guiding developers on mounting mTLS client certificates into Docker containers and passing virtual keys for App Servers.

**Independent Test**: Click "Hướng dẫn Docker Workload" in ClientsTable; verify dialog opens with copyable Docker Compose snippet, volume mounts, and curl verification command.

### Implementation for User Story 2
- [X] T003 [P] [US2] Implement `DockerDeploymentGuideDialog` in `web/src/features/clients/components/docker-deployment-guide-dialog.tsx` with Docker Compose volumes, environment variables, and verification curl commands
- [X] T004 [US2] Export `DockerDeploymentGuideDialog` in `web/src/features/clients/index.ts`
- [X] T005 [US2] Add "Hướng dẫn Docker Workload" button with icon `Container` to the top action bar in `web/src/features/clients/components/clients-table.tsx`

**Checkpoint**: User Story 2 complete; Docker machine workload guide is accessible and testable.

---

## Phase 3: User Story 3 - In-Memory SDK Quickstart Modal in Vault (Priority: P2)

**Goal**: Provide a quickstart dialog inside the project Vault view showing zero-.env dynamic secret loading into RAM via `dut-vault-sdk`.

**Independent Test**: Click "Tích hợp SDK" on VaultView; verify dialog opens pre-filled with project ID and scopes, with copyable Python code.

### Implementation for User Story 3
- [X] T006 [P] [US3] Implement `SdkQuickstartDialog` in `web/src/features/vault/components/sdk-quickstart-dialog.tsx` with zero-.env in-memory loading snippets, pip installation instructions, and hot-reload listeners
- [X] T007 [US3] Export `SdkQuickstartDialog` in `web/src/features/vault/components/index.ts` and `web/src/features/vault/index.ts`
- [X] T008 [US3] Add "Tích hợp SDK" button with icon `Terminal` to the header action bar in `web/src/features/vault/components/vault-view.tsx`

**Checkpoint**: User Story 3 complete; SDK quickstart dialog integrated seamlessly into Vault.

---

## Phase 4: Polish & Quality Gates

**Purpose**: Cross-cutting validation, documentation, and type checks

- [X] T009 [P] Update `docs/CHECKLIST_REMAINING_TASKS.md` marking Phase 4 tasks as completed
- [X] T010 Run frontend TypeScript validation: `cd web && pnpm tsc --noEmit`
- [X] T011 Run code formatting and linting: `uv run ruff check .` and `uv run ruff format --check .`
- [X] T012 Run automated test suite: `uv run pytest tests/` and `make test-e2e`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (US1)**: Can start immediately.
- **Phase 2 (US2)**: Can start in parallel with US1.
- **Phase 3 (US3)**: Can start in parallel with US1/US2.
- **Phase 4 (Polish)**: Depends on completion of US1, US2, US3.

### Parallel Opportunities
- `T001`, `T003`, and `T006` can be authored in parallel as they touch independent component files.
