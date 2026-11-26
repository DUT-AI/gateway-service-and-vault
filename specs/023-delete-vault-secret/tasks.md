---

description: "Task list for Delete Vault Environment Variable"
---

# Tasks: Delete Vault Environment Variable

**Input**: Design documents from `specs/023-delete-vault-secret/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/delete-secret-api.md`, `quickstart.md`

**Organization**: Tasks are grouped by user story, adhering to Constitution v2.4.0.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Foundational Repository & DTO Extensions

- [x] T001 [P] Add `delete_secret(project_id: str, scope_name: str, key: str) -> bool` to `ISecretRepository` in `modules/vault/domain/interfaces.py` and implement in `modules/vault/repository/secret_repository.py` (no `session.commit()`)
- [x] T002 [P] Add `DeleteSecretResponse` to `modules/vault/dtos/vault_dtos.py`

---

## Phase 2: User Story 1 & 2 - Delete Secret Use Case, RBAC & API Route (Priority: P1/P2) 🎯 MVP

- [x] T003 [US1] Create `DeleteSecretUseCase` in `modules/vault/use_cases/delete_secret.py` (enforcing `require_permission_for_identity`, raising `NotFoundError` / `EntityNotFoundError` if secret missing, and publishing SSE `ConfigChangeEvent` via `IVaultBroadcaster`)
- [x] T004 [US1] Export `DeleteSecretUseCase` in `modules/vault/use_cases/__init__.py` and register in `modules/vault/di.py`
- [x] T005 [US1] Add `DELETE /projects/{project_id}/secrets` (`scope_name`, `key` query params) in `apps/api/routers/vault/secrets.py` with `get_current_user_context` + `ensure_project_access` + 3-tier RBAC (`user_ctx.is_other`)

---

## Phase 3: User Story 1 & 3 - Frontend Delete Action, Confirmation Dialog & SSE Sync (Priority: P1/P3)

- [x] T006 [P] [US1] Add `deleteSecret(projectId, scopeName, key)` in `web/src/features/vault/services/vault-service.ts` and `useDeleteSecretMutation(projectId)` in `web/src/features/vault/hooks/use-vault-queries.ts`
- [x] T007 [P] [US1] Create `DeleteSecretDialog` component in `web/src/features/vault/components/delete-secret-dialog.tsx`
- [x] T008 [US1] Add Delete (`Trash2`) button per row in `web/src/features/vault/components/secrets-table.tsx` and wire `DeleteSecretDialog` in `web/src/features/vault/components/vault-view.tsx`

---

## Phase 4: Verification, Type Sync & Quality Gates

- [x] T009 [P] Run `make api-types` and `cd web && pnpm typecheck && npx eslint` on all modified/created frontend files
- [x] T010 Write integration test suite `tests/integration/test_delete_vault_secret.py` covering `ADMIN`, assigned `PROJECT_DEVELOPER`, unassigned `403`, `RoleTier.OTHER` (`200` on permitted key, `403` on unpermitted key), and `404` on missing secret
- [x] T011 Run `uv run ruff check --fix && uv run ruff format` and `uv run pytest tests/integration/test_delete_vault_secret.py tests/integration/test_vault_rbac.py tests/test_clean_architecture_purity.py`
