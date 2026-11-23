---
description: "Task list for Web Phase 3 - Real-Time Vault Hot-Reload Stream (SSE Live Sync)"
---

# Tasks: Web Phase 3 - Real-Time Vault Hot-Reload Stream (SSE Live Sync)

**Input**: Design documents from `/specs/009-web-vault-sse-sync/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/stream-api.md`, `quickstart.md`  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.  

## Format: `- [X] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Exact file paths included in all task descriptions

---

## Phase 1: Setup (Backend Compatibility & Stream Types)

**Purpose**: Update SSE streaming endpoint parameter support and establish client-side stream types

- [X] T001 Update `stream_project_secrets` in `apps/api/routers/vault/stream.py` to accept `identity_id: str | None = Query(default=None)` as a fallback for browser EventSource connections
- [X] T002 [P] Define `SseConnectionStatus`, `SseConnectedEvent`, `SseSecretUpdateEvent`, `SsePingEvent`, and `VaultSseState` in `web/src/features/vault/types/stream-types.ts`
- [X] T003 Re-export stream types in `web/src/features/vault/types/index.ts` and `web/src/features/vault/index.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core SSE connection management hook, heartbeat watchdog, and backoff reconnection algorithm

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Implement `useVaultSse` hook in `web/src/features/vault/hooks/use-vault-sse.ts` with EventSource lifecycle, 35s heartbeat watchdog timer, exponential backoff with jitter (1s base, 10s max), page visibility handler, and clean unmount teardown
- [X] T005 Export `useVaultSse` hook in `web/src/features/vault/hooks/index.ts` and `web/src/features/vault/index.ts`

**Checkpoint**: Data & stream connection foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Real-Time SSE Stream Hook & Live Sync Status Indicator (Priority: P1) 🎯 MVP

**Goal**: Authenticated developers viewing a project's Vault workspace see an active visual indicator showing real-time SSE stream connectivity (Live Connected, Reconnecting, or Disconnected).

**Independent Test**: Navigate to `/projects/[id]` -> Open "Biến môi trường (Vault)" tab -> Observe `LiveSyncStatusBadge` displaying a pulsating green dot with "Live Sync" and connected status -> Verify active SSE stream in browser network tab.

### Implementation for User Story 1

- [X] T006 [P] [US1] Implement `LiveSyncStatusBadge` component in `web/src/features/vault/components/live-sync-status-badge.tsx` rendering green pulsing dot for "Live Sync" (connected), amber dot for "Đang kết nối lại..." (connecting), and gray dot for "Ngoại tuyến" (disconnected) with tooltip
- [X] T007 [US1] Mount `useVaultSse` and `LiveSyncStatusBadge` into `VaultView` toolbar in `web/src/features/vault/components/vault-view.tsx`

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently (MVP ready!)

---

## Phase 4: User Story 2 - Auto Cache Invalidation & Seamless Table Hot-Reload (Priority: P2)

**Goal**: When a secret is created, updated, or rotated in the project, all connected client tables automatically invalidate cache, re-fetch updated values in under 3 seconds, and apply a transient pulse highlight to changed rows.

**Independent Test**: Open the project Vault in Window A and Window B -> Update a secret in Window A -> Window B automatically updates its table in < 3 seconds and highlights the changed row with a blue glow.

### Implementation for User Story 2

- [X] T008 [US2] Connect `useVaultSse` to TanStack Query client to automatically invalidate `VAULT_KEYS.secrets(projectId)` and `VAULT_KEYS.scopes(projectId)` upon receiving `event: secret_update`
- [X] T009 [P] [US2] Update `useVaultSse` in `web/src/features/vault/hooks/use-vault-sse.ts` to manage `highlightedKeys: Set<string>` state fading after 2500ms
- [X] T010 [US2] Update `SecretsTable` in `web/src/features/vault/components/secrets-table.tsx` to accept `highlightedKeys?: Set<string>` and apply transient blue highlight animation (`ring-2 ring-blue-500/50 bg-blue-50/40 transition-all duration-700`) to changed secret rows
- [X] T011 [US2] Pass `highlightedKeys` from `useVaultSse` through `VaultView` to `SecretsTable` in `web/src/features/vault/components/vault-view.tsx`

**Checkpoint**: At this point, User Stories 1 AND 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Live Audit Feed & Real-Time Change Notifications (Priority: P3)

**Goal**: Users receive real-time Sonner toast notifications when secrets change and can open a live audit feed drawer showing the history of recent configuration change events with relative timestamps.

**Independent Test**: Update a secret in Window A -> In Window B, observe Sonner toast *"Admin vừa cập nhật biến [KEY] (Scope: [SCOPE])"* -> Click "Nhật ký Live" button -> View recent events list showing actor, scope, and relative time.

### Implementation for User Story 3

- [X] T012 [US3] Integrate real-time Sonner toast notifications in `useVaultSse` on `secret_update` events showing actor, scope name, and changed keys list
- [X] T013 [US3] Implement `LiveAuditFeed` component in `web/src/features/vault/components/live-audit-feed.tsx` displaying chronological event cards with actor badge, scope badge, changed keys, relative time formatting ("vừa xong", "1 phút trước"), and a live sync pause/resume toggle switch
- [X] T014 [US3] Wire `LiveAuditFeed` button and popover into `VaultView` toolbar in `web/src/features/vault/components/vault-view.tsx`

**Checkpoint**: All three user stories are fully functional and integrated.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Module exports, responsive verification, and automated build verification

- [X] T015 [P] Export all new components in `web/src/features/vault/components/index.ts` and public feature entry point in `web/src/features/vault/index.ts`
- [X] T016 Run quickstart validation from `specs/009-web-vault-sse-sync/quickstart.md` (`pnpm --prefix web typecheck && pnpm --prefix web build && uv run pytest`)
- [X] T017 Validate responsive mobile viewports (<768px), pause/resume stream toggling, and clean listener garbage collection

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start immediately after Foundational (MVP!)
  - User Story 2 (P2): Depends on Foundational hook & US1 table view
  - User Story 3 (P3): Depends on Foundational hook & US1/US2 toolbar
- **Polish (Phase 6)**: Depends on all user stories being complete
