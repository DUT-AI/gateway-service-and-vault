# Feature Specification: Web Phase 3 - Real-Time Vault Hot-Reload Stream (SSE Live Sync)

**Feature Branch**: `009-web-vault-sse-sync`  
**Created**: 2026-11-23  
**Status**: Ready for Planning  
**Input**: Phase 3 requirements from `docs/WEB_ROADMAP.md` ("Giai Đoạn 3: Real-Time In-Memory Hot-Reload Stream (SSE Live Sync) - Giám sát thời gian thực việc nạp biến môi trường; ứng dụng nhận thay đổi cấu hình dưới 5 giây không cần restart").

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Real-Time SSE Stream Hook & Live Sync Status Indicator (Priority: P1) 🎯 MVP

As an authenticated developer or DevOps engineer viewing a project's Vault workspace, I want a live connection indicator showing the real-time synchronization state with the backend SSE stream, so that I know immediately whether configuration updates are being streamed live without manual polling or browser refreshes.

**Why this priority**: Core architectural prerequisite for real-time capabilities. Without the SSE client hook and connection lifecycle management, real-time sync cannot occur.

**Independent Test**: Navigate to `/projects/[id]` -> Open the "Biến môi trường (Vault)" tab -> Observe the `LiveSyncStatusBadge` displaying a pulsing green dot with "Live Sync" and connected status -> Inspect browser network tab verifying active SSE connection to `/api/v1/vault/projects/{id}/stream`.

**Acceptance Scenarios**:
1. **Given** a user opening a project workspace Vault tab, **When** the page mounts, **Then** `useVaultSse` establishes a connection to `GET /api/v1/vault/projects/{id}/stream`.
2. **Given** an active connection, **When** the backend transmits `event: connected`, **Then** the badge state transitions to `connected` (pulsing green dot, text "Live Sync").
3. **Given** regular heartbeat events from the server, **When** `event: ping` arrives, **Then** the hook updates `lastPing` timestamp and remains in `connected` status.
4. **Given** a network disconnection or server restart, **When** the connection drops, **Then** the status transitions to `connecting` / `reconnecting` (amber dot) and attempts reconnection using exponential backoff (1s, 2s, 4s up to 10s max).
5. **Given** the user navigating away from the project workspace, **When** the component unmounts, **Then** the SSE connection is cleanly closed without memory leaks or dangling listeners.

---

### User Story 2 - Auto Cache Invalidation & Seamless Table Hot-Reload (Priority: P2)

As a team member working in a shared project workspace, I want the secrets table to update automatically when another user or automated CI/CD pipeline modifies a configuration secret, so that my view is always synchronized in under 3 seconds without requiring a manual page reload.

**Why this priority**: Directly fulfills Constitution Principle VII ("Real-Time In-Memory Hot-Reload < 5s Latency"), ensuring multi-user collaboration consistency and zero stale configuration reads.

**Independent Test**: Open the project Vault tab in two separate browser windows (Window A and Window B) -> In Window A, add or edit a secret (e.g. `API_TIMEOUT=30s`) -> Observe Window B receiving the update in < 3 seconds: the table automatically updates and briefly flashes to highlight the modified row.

**Acceptance Scenarios**:
1. **Given** two active sessions viewing the same project Vault, **When** Session A updates a secret via `POST /api/v1/vault/projects/{id}/secrets`, **Then** Session B receives `event: secret_update` over the SSE stream.
2. **Given** `event: secret_update` received, **When** processed by `useVaultSse`, **Then** the hook triggers TanStack Query cache invalidation for `VAULT_KEYS.secrets(projectId)` and `VAULT_KEYS.scopes(projectId)`.
3. **Given** cache invalidation, **When** new data is refetched, **Then** the table re-renders seamlessly with the updated value and version without disrupting the user's current scroll position or search filter.
4. **Given** an updated secret key, **When** the new row renders, **Then** a brief highlight effect (e.g. blue ring/glow fading over 2 seconds) visually calls attention to the changed configuration.

---

### User Story 3 - Live Audit Feed & Real-Time Change Notifications (Priority: P3)

As a project administrator or security engineer, I want real-time notification toasts and a live audit activity log of recent secret change events, so that I can audit who changed which secret, in what scope, and at what time.

**Why this priority**: Provides situational awareness, security transparency, and immediate operational feedback during secret rotation or incident response.

**Independent Test**: In Window A, update a secret `STRIPE_KEY` in scope `Payment` -> In Window B, observe a real-time notification toast: *"Admin vừa cập nhật biến STRIPE_KEY (Scope: Payment)"* -> Click "Nhật ký Live" (Live Audit Feed) button -> View timeline list showing recent change events with actor, scope, changed keys, and timestamp.

**Acceptance Scenarios**:
1. **Given** an active SSE stream, **When** a `secret_update` event arrives, **Then** a Sonner toast notification appears displaying the actor, scope name, and changed keys list.
2. **Given** the Vault toolbar, **When** clicking the "Nhật ký Live" (Live Feed) button, **Then** a collapsible panel or drawer (`LiveAuditFeed`) opens.
3. **Given** the `LiveAuditFeed` panel, **When** open, **Then** it renders a chronological feed of recent change events (last 20 events) showing event ID, actor badge, scope badge, changed keys, version number, and relative time (e.g. "vừa xong", "2 phút trước").
4. **Given** the user wanting to pause live sync during debugging, **When** toggling the pause switch in the badge/feed, **Then** stream events are buffered or paused until resumed.

---

### Edge Cases

- **Heartbeat Timeout**: If no `ping` or event is received for 30 seconds (2 missed heartbeat intervals), the hook automatically assumes a silent connection drop and re-initiates the connection.
- **Granular Key Permission Filtering**: If a user lacks permission for the specific changed key, the backend stream dispatcher filters out the event, and the user receives nothing (enforcing Zero-Trust least-privilege).
- **Background Tab / Page Visibility**: When the browser tab is hidden (`document.hidden`), connection maintains or cleanly reconnects when the tab becomes visible again (`visibilitychange` event).
- **Stream Reconnection Throttling**: Exponential backoff prevents DDoS spikes on the Redis/FastAPI server when network connectivity flickers.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Domain 1: SSE Streaming Hook & Connection Management
- **FR-001**: System MUST provide a custom React hook `useVaultSse(projectId, options)` that manages connection to `GET /api/v1/vault/projects/{id}/stream`.
- **FR-002**: System MUST track connection state (`"connected" | "connecting" | "disconnected" | "error"`) and expose it to consumer components.
- **FR-003**: System MUST parse SSE data packets for `event: connected`, `event: secret_update`, and `event: ping`.
- **FR-004**: System MUST implement exponential backoff reconnection with random jitter (1s base, 2x factor, 10s maximum cap).
- **FR-005**: System MUST clean up EventSource/stream readers when component unmounts or `projectId` changes.

#### Domain 2: Visual Connection State & Auto Invalidation
- **FR-006**: System MUST provide a `LiveSyncStatusBadge` component with distinct visual states: Green (Live Connected), Amber (Connecting/Reconnecting), Gray (Disconnected).
- **FR-007**: System MUST invalidate TanStack Query cache keys for secrets and scopes upon receiving `secret_update`.
- **FR-008**: System MUST highlight newly modified rows in `SecretsTable` with a transient visual pulse animation.

#### Domain 3: Live Audit Notifications & Feed
- **FR-009**: System MUST trigger an informative toast notification via `Sonner` on `secret_update` events showing the actor, scope name, and changed keys.
- **FR-010**: System MUST maintain an in-memory buffer of recent change events (up to 20 events) within the session.
- **FR-011**: System MUST provide a `LiveAuditFeed` component displaying chronological history of config events with relative timestamps and actor metadata.
- **FR-012**: System MUST allow users to manually pause and resume live streaming via a toggle control.

---

### Key Entities

- **VaultStreamEvent**: Union of parsed SSE events:
  - `ConnectedEvent`: `{ project_id: string, status: string, timestamp: string }`
  - `SecretUpdateEvent`: `{ event_id: string, project_id: string, scope_name: string, changed_keys: string[], new_version: number, actor: string, timestamp: string }`
  - `PingEvent`: `{ timestamp: string }`
- **LiveSyncState**: `{ status: "connected" | "connecting" | "disconnected" | "error", lastPing: Date | null, events: SecretUpdateEvent[], isPaused: boolean }`

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Configuration updates in Window A synchronize to Window B within **< 3.0 seconds** (exceeding Constitution Principle VII requirement of < 5s).
- **SC-002**: Connection drops reconnect automatically within 2 seconds of network restoration.
- **SC-003**: Zero memory leaks: Event listeners and stream readers are completely cleaned up on page transitions.
- **SC-004**: Zero full page reloads: Cache invalidation updates the table smoothly without UI stutter or scroll reset.
- **SC-005**: 100% type safety: passes `pnpm --prefix web typecheck` and `pnpm --prefix web build` with zero errors.
