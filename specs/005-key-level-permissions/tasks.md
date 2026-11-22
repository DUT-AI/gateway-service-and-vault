---
description: "Task list for Granular Key-Level Secret Permissions feature implementation"
---

# Tasks: Granular Key-Level Secret Permissions

**Input**: Design documents from `/specs/005-key-level-permissions/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`  
**Tests**: Included as specified in spec criteria and quality gates.  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Exact file paths included in all task descriptions

---

## Phase 1: Setup (Shared Infrastructure & Migrations)

**Purpose**: Database schema creation and migration setup

- [X] T001 [P] Create Alembic migration script in `migrations/versions/003_key_permissions.py` creating `key_permissions` table with foreign key to `projects.id`, unique constraint on `(project_id, identity_id, secret_key)`, and composite index on `(project_id, identity_id)`
- [X] T002 Apply Alembic migration `003_key_permissions` to running PostgreSQL database via `uv run alembic upgrade head`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain entities, SQLAlchemy models, DTOs, and repository protocols that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Define pure domain entity `KeyPermissionEntity` in `modules/vault/domain/entities.py` with fields: `id: str`, `project_id: str`, `identity_id: str`, `secret_key: str`, `identity_type: str`, `granted_by: str`, `created_at: datetime`, and `updated_at: datetime` (zero framework imports)
- [X] T004 [P] Define SQLAlchemy model `KeyPermissionModel` in `modules/vault/models/permission.py` and export in `modules/vault/models/__init__.py`
- [X] T005 [P] Define Pydantic v2 schemas `GrantKeyPermissionRequest`, `RevokeKeyPermissionRequest`, `KeyPermissionResponse`, and `IdentityPermissionsResponse` in `modules/vault/dtos/vault_dtos.py`
- [X] T006 [P] Update `ISecretRepository` interface protocol in `modules/vault/domain/interfaces.py` adding methods `grant_key_permission`, `revoke_key_permission`, `list_permissions_by_identity`, and `get_permitted_keys_for_identity`
- [X] T007 Implement key permission persistence queries in `SqlSecretRepository` in `modules/vault/repository/secret_repository.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Identity-Based Key-Level Secret Retrieval (Priority: P1) 🎯 MVP

**Goal**: Enforce deny-by-default key-level authorization when reading secrets. Return ONLY granted keys, omit unpermitted keys completely, and return 403 Forbidden on unauthorized direct single-key requests.

**Independent Test**: Create 2 secrets in a project (`DATABASE_URL`, `STRIPE_KEY`). Grant Identity A access only to `DATABASE_URL`. Read secrets as Identity A -> verify response contains only `DATABASE_URL` and excludes `STRIPE_KEY`.

### Tests for User Story 1

- [X] T008 [P] [US1] Create integration test in `tests/integration/test_granular_key_permissions.py` validating identity-based key filtering, omission of ungranted keys, and 403 Forbidden on unauthorized single-key request

### Implementation for User Story 1

- [X] T009 [US1] Update `GetSecretsByScopeUseCase` in `modules/vault/use_cases/vault_use_cases.py` to resolve caller permitted keys from repository and filter decrypted secrets in RAM, raising `ScopePermissionDeniedError` if an unauthorized single key is requested
- [X] T010 [US1] Update `GET /api/v1/vault/projects/{project_id}/secrets` route in `apps/api/routers/vault_router.py` to extract `X-Identity-Id` header (defaulting to anonymous), remove legacy role checks, and pass optional `key` filter parameter

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently (MVP ready!)

---

## Phase 4: User Story 2 - Key Permission Management (Grant, Revoke & List) (Priority: P2)

**Goal**: Allow administrators to grant, revoke, and query key permissions for specific identities in a project.

**Independent Test**: Grant Identity C permission for a key. Verify identity can read the key. Revoke the key. Verify identity can no longer read the key.

### Tests for User Story 2

- [X] T011 [P] [US2] Create unit test in `tests/unit/test_key_permissions_use_cases.py` testing `GrantKeyPermissionUseCase`, `RevokeKeyPermissionUseCase`, and `ListIdentityPermissionsUseCase`

### Implementation for User Story 2

- [X] T012 [P] [US2] Implement `GrantKeyPermissionUseCase`, `RevokeKeyPermissionUseCase`, and `ListIdentityPermissionsUseCase` in `modules/vault/use_cases/vault_use_cases.py`
- [X] T013 [US2] Register new permission use cases in Dishka `VaultProvider` in `modules/vault/di.py`
- [X] T014 [US2] Implement `POST`, `DELETE`, and `GET /api/v1/vault/projects/{project_id}/permissions` endpoints in `apps/api/routers/vault_router.py`

**Checkpoint**: At this point, User Stories 1 AND 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Key-Level Filtered SSE Event Streaming (Priority: P3)

**Goal**: Filter real-time SSE stream events so that clients only receive `secret_update` notifications if at least one changed key is permitted to their identity.

**Independent Test**: Connect Identity A to SSE stream. Update a secret that Identity A does not have access to -> verify zero notifications received. Update a secret Identity A has access to -> verify notification received.

### Tests for User Story 3

- [X] T015 [P] [US3] Create integration test in `tests/integration/test_sse_stream_key_filtering.py` verifying stream event filtering per identity

### Implementation for User Story 3

- [X] T016 [US3] Update `GET /api/v1/vault/projects/{project_id}/stream` in `apps/api/routers/vault_router.py` to extract `X-Identity-Id`, query permitted keys, and filter out `secret_update` notifications for unauthorized keys

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Architectural validation, documentation, and end-to-end quickstart execution

- [X] T017 Verify Clean Architecture purity gate in `tests/test_clean_architecture_purity.py` ensuring zero framework imports in `modules/vault/domain/`
- [X] T018 [P] Update documentation in `docs/ROADMAP.md` and feature specs with granular key-level permission model
- [X] T019 Execute quickstart validation steps from `specs/005-key-level-permissions/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start immediately after Foundational (MVP!)
  - User Story 2 (P2): Can run in parallel with or after US1
  - User Story 3 (P3): Depends on US1 permission resolution and SSE stream endpoint
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- Tasks T003, T004, T005, T006 can run in parallel in Phase 2 across different files.
- Tests T008, T011, T015 can be authored in parallel.
- Documentation update T018 can run in parallel with T017.

---

## Parallel Example: User Story 2

```bash
# Launch test and implementation for User Story 2 together:
Task: "Create unit test in tests/unit/test_key_permissions_use_cases.py"
Task: "Implement GrantKeyPermissionUseCase, RevokeKeyPermissionUseCase in modules/vault/use_cases/vault_use_cases.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Alembic migration)
2. Complete Phase 2: Foundational (Entities, Model, Protocol, Repository)
3. Complete Phase 3: User Story 1 (Enforce key-level filtering on secret read)
4. **STOP and VALIDATE**: Test User Story 1 independently with `test_granular_key_permissions.py`.
5. Deliver MVP!

### Incremental Delivery (User Stories 2, 3 & Polish)

1. Add Phase 4: User Story 2 (Admin permission management endpoints).
2. Add Phase 5: User Story 3 (SSE stream key-level filtering).
3. Complete Phase 6: Polish & quickstart validation.
4. Run full test suite with `uv run pytest`.
