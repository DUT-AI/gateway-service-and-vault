---
description: "Task list for Web Phase 2 - Dynamic Vault Management & Key-Level ACL"
---

# Tasks: Web Phase 2 - Dynamic Vault Management & Key-Level ACL

**Input**: Design documents from `/specs/008-web-vault-acl/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/vault-api.md`, `quickstart.md`  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.  

## Format: `- [X] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Exact file paths included in all task descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish feature directories and reusable UI component primitives

- [X] T001 Create feature directory structure in `web/src/features/vault/` (`types/`, `services/`, `hooks/`, `components/`)
- [X] T002 [P] Implement `Checkbox` component in `web/src/components/ui/checkbox.tsx` and export it in `web/src/components/ui/index.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models, HTTP service clients, and React Query hooks required by all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Define `Scope`, `GetSecretsResponse`, `CreateSecretPayload`, `KeyPermission`, `UserOption` types and normalized entities (`FlatSecretItem`, `KeyPermissionItem`) in `web/src/features/vault/types/index.ts`
- [X] T004 [P] Implement `vaultService` HTTP client methods (`listScopes`, `getSecrets`, `createSecret`, `listPermissions`, `grantPermission`, `revokePermission`) in `web/src/features/vault/services/vault-service.ts`
- [X] T005 [P] Implement `userDirectoryService` HTTP client method (`listUserOptions`) in `web/src/features/vault/services/user-directory-service.ts`
- [X] T006 Implement TanStack React Query hooks (`useScopesQuery`, `useSecretsQuery`, `useSaveSecretMutation`) with query key cache management in `web/src/features/vault/hooks/use-vault-queries.ts`
- [X] T007 [P] Implement TanStack React Query hooks (`useIdentityPermissionsQuery`, `useGrantPermissionMutation`, `useRevokePermissionMutation`) in `web/src/features/vault/hooks/use-permissions-queries.ts`
- [X] T008 [P] Implement `useUserOptionsQuery` hook in `web/src/features/vault/hooks/use-user-options-query.ts`
- [X] T009 Export all types, services, and query hooks in `web/src/features/vault/index.ts`

**Checkpoint**: Data foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Scope Tabs & Encrypted Secret Management Table (Priority: P1) 🎯 MVP

**Goal**: Authenticated developers can view their project's environment configurations grouped by Scope tabs, inspect masked values (`••••••••••••`), toggle reveal/hide on demand, and copy values to clipboard with instant toast confirmation.

**Independent Test**: Navigate to `/projects/[id]` -> Open the "Biến môi trường (Vault)" tab -> Verify scope tabs and secrets table render -> Toggle "Eye" icon to unmask secret value -> Click "Copy" icon and verify value copied to clipboard with toast notification.

### Implementation for User Story 1

- [X] T010 [P] [US1] Implement `ScopeTabs` component in `web/src/features/vault/components/scope-tabs.tsx` rendering scope tabs with active indicators, "Tất cả" (All) tab, and badge count
- [X] T011 [P] [US1] Implement `SecretsTable` component in `web/src/features/vault/components/secrets-table.tsx` with default masked values (`••••••••••••`), reveal/hide eye toggle, copy-to-clipboard action with Sonner toast, search filter input, skeleton loader rows, and empty state
- [X] T012 [US1] Implement `VaultView` container component in `web/src/features/vault/components/vault-view.tsx` integrating `ScopeTabs`, `SecretsTable`, search filter state, and toolbar action buttons
- [X] T013 [US1] Mount `VaultView` in `web/src/features/projects/components/project-workspace-tabs.tsx` replacing the Vault placeholder card

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently (MVP ready!)

---

## Phase 4: User Story 2 - Interactive Secret Creation & Edit Dialog (Priority: P2)

**Goal**: Users can add a new secret or update an existing secret through an accessible modal dialog with Scope selection, upper snake_case key validation, and secret value toggle.

**Independent Test**: Click "Thêm biến mới", select Scope "Database", enter Key `DB_PASSWORD` and Value `secret123`, submit form -> Modal closes, success toast appears, and the new secret row immediately appears under the Database scope.

### Implementation for User Story 2

- [X] T014 [P] [US2] Implement Zod validation schema `createSecretSchema` in `web/src/features/vault/types/form-schemas.ts` enforcing `^[A-Z0-9_]+$` key validation and non-empty values
- [X] T015 [US2] Implement `SecretDialog` component in `web/src/features/vault/components/secret-dialog.tsx` using `Dialog`, `react-hook-form`, scope select/input, key uppercase formatting, value password toggle, submit loading spinner, and Sonner toast
- [X] T016 [US2] Wire `SecretDialog` into `VaultView` toolbar "Thêm biến mới" button and row-level "Sửa" edit actions in `web/src/features/vault/components/vault-view.tsx`

**Checkpoint**: At this point, User Stories 1 AND 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Granular Key Permissions Matrix Modal (Priority: P3)

**Goal**: Administrators can view an access control matrix for any user from the central directory, check/uncheck individual secret keys, and have permissions granted or revoked in real time.

**Independent Test**: Click "Phân quyền truy cập" -> Select a user from central directory dropdown -> View secret key checklist -> Check a key to grant permission -> Uncheck to revoke -> Verify immediate permission update via API.

### Implementation for User Story 3

- [X] T017 [US3] Implement `KeyPermissionMatrixModal` component in `web/src/features/vault/components/key-permission-matrix-modal.tsx` with user selector dropdown (`useUserOptionsQuery`), checkbox matrix of project secret keys (`useIdentityPermissionsQuery`), grant and revoke mutations, and toast notifications
- [X] T018 [US3] Wire `KeyPermissionMatrixModal` trigger button into `VaultView` toolbar in `web/src/features/vault/components/vault-view.tsx`

**Checkpoint**: All three user stories are fully functional and integrated.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Component export packaging, responsive verification, and automated build verification

- [X] T019 [P] Export all vault components in `web/src/features/vault/components/index.ts` and public feature exports in `web/src/features/vault/index.ts`
- [X] T020 Run quickstart validation from `specs/008-web-vault-acl/quickstart.md` (`pnpm --prefix web typecheck && pnpm --prefix web build && uv run pytest`)
- [X] T021 Validate responsive mobile viewports (<768px) and accessible keyboard navigation across `SecretsTable`, `SecretDialog`, and `KeyPermissionMatrixModal`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start immediately after Foundational (MVP!)
  - User Story 2 (P2): Depends on Foundational mutation hook & US1 view
  - User Story 3 (P3): Depends on Foundational permissions hooks & US1 key list
- **Polish (Phase 6)**: Depends on all user stories being complete
