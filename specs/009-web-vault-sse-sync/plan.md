# Implementation Plan: Web Phase 3 - Real-Time Vault Hot-Reload Stream (SSE Live Sync)

**Branch**: `009-web-vault-sse-sync` | **Date**: 2026-11-23 | **Spec**: [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/009-web-vault-sse-sync/spec.md)

**Input**: Feature specification from `/specs/009-web-vault-sse-sync/spec.md` and Phase 3 roadmap from `docs/WEB_ROADMAP.md`.

---

## Summary

Implement the client-side Real-Time Server-Sent Events (SSE) streaming infrastructure for the Dynamic Vault Engine. This connects the web application to the backend's Redis Pub/Sub SSE broadcaster (`GET /api/v1/vault/projects/{project_id}/stream`), monitors live connection health with heartbeat pings and auto-reconnect backoff, automatically invalidates TanStack Query caches to hot-reload secrets in under 3 seconds without full page refreshes, highlights updated secret rows visually, and provides a real-time live audit feed of configuration change events.

---

## Technical Context

**Language/Version**: TypeScript 5.x / Next.js 16.2.4 (App Router, React 19.2.4, Turbopack) & Python 3.12 (FastAPI backend)  
**Primary Dependencies**: `@tanstack/react-query` v5, `axios`, `sonner`, `lucide-react`, native browser `EventSource` and `ReadableStream`  
**Storage & Transport**: Redis Pub/Sub channel (`vault:project:{project_id}:changes`), FastAPI `StreamingResponse` (media type `text/event-stream`), in-memory React event buffer (last 20 events)  
**Testing**: `pnpm --prefix web typecheck`, `pnpm --prefix web build`, `uv run pytest`  
**Target Platform**: Modern desktop and mobile web browsers (Chrome, Firefox, Safari, Edge)  
**Project Type**: Real-time reactive web feature inside modular monolith architecture  
**Performance Goals**: 
- **< 3.0 seconds** synchronization latency from mutation in Window A to table update in Window B (exceeding Constitution Principle VII constraint of < 5s).
- **< 2.0 seconds** automatic reconnection upon network restoration.
- Zero layout shifts and zero scroll resets during table hot-reloads.
**Constraints**:
- Heartbeat watchdog: detect silent drops within 35s (2 missed pings).
- Granular key permission filtering enforced by backend stream dispatcher.
- Complete cleanup of listeners/readers on unmount to prevent memory leaks.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Compliance Status | Justification / Notes |
|---|---|---|---|
| **I. Clean Architecture** | Pure domain layer | **PASS** | Domain events (`ConfigChangeEvent`) remain pure dataclasses; SSE routing lives strictly in API delivery layer. |
| **II. Modular Monolith** | Bounded context isolation | **PASS** | Vault broadcasting and client sync logic are completely encapsulated in the `vault` feature module. |
| **III. Transactional Outbox** | Resilient background delivery | **PASS** | Secret updates write to database and publish to Redis Pub/Sub within the use case transaction boundary. |
| **IV. Offline Type Sync** | Schema derived from single source of truth | **PASS** | Event types map directly to `ConfigChangeEvent.to_dict()` JSON payload structure. |
| **V. Pure SSO** | Identity context and integer IDs | **PASS** | Caller identity passed via query param or header (`identity_id: str(user.id)`). |
| **VI. Dynamic Vault & ACL** | Granular key-level access control | **PASS** | Stream dispatcher filters events: callers only receive updates for keys they are permitted to read. |
| **VII. Real-Time Hot-Reload** | Live updates < 5s latency without restart | **PASS** | Fulfills this principle completely: client updates UI in under 3 seconds via SSE event-driven cache invalidation. |
| **VIII. Zero-Trust Gateway** | Secure upstream communication | **PASS** | Prepares ground for Phase 4 gateway integration. |

---

## Project Structure

### Documentation (this feature)

```text
specs/009-web-vault-sse-sync/
├── spec.md              # Feature specification and prioritized user stories
├── plan.md              # This architectural implementation plan
├── research.md          # SSE transport, backoff reconnection, and pulse highlighting
├── data-model.md        # Event payload schemas, connection state machine
├── contracts/
│   └── stream-api.md    # API contract for GET /vault/projects/{id}/stream
├── quickstart.md        # Multi-window verification guide
└── tasks.md             # Implementation checklist (/speckit-tasks output)
```

### Source Code Layout

```text
# Backend API Layer
apps/api/routers/vault/
└── stream.py                            # Add identity_id query param support for EventSource

# Frontend Web Application
web/src/
├── features/
│   └── vault/
│       ├── types/
│       │   ├── stream-types.ts          # SseConnectionStatus, SseSecretUpdateEvent, VaultSseState
│       │   └── index.ts                 # Export stream types
│       ├── hooks/
│       │   ├── use-vault-sse.ts         # Core SSE stream hook with exponential backoff & watchdog
│       │   └── index.ts                 # Export hooks
│       ├── components/
│       │   ├── live-sync-status-badge.tsx # Visual status badge (Live Connected / Reconnecting / Offline)
│       │   ├── live-audit-feed.tsx      # Chronological audit feed of change events with relative times
│       │   ├── secrets-table.tsx        # Add highlightedKeys prop for transient pulse highlight
│       │   ├── vault-view.tsx           # Integrate badge, live feed button, and SSE stream hook
│       │   └── index.ts                 # Export components
│       └── index.ts                     # Feature public exports
```

---

## Architectural Breakdown & User Stories

### Phase 1: Foundational Backend Query Param & Stream Types
- Update `apps/api/routers/vault/stream.py` to accept `identity_id: str | None = Query(default=None)` as a fallback alongside `x_identity_id` header, ensuring standard browser `EventSource` can transmit identity context cleanly.
- Define `SseConnectionStatus`, `SseSecretUpdateEvent`, `SseConnectedEvent`, `SsePingEvent`, and `VaultSseState` in `web/src/features/vault/types/stream-types.ts`.
- Export stream types from `web/src/features/vault/types/index.ts`.

### Phase 2: User Story 1 (P1 - MVP) - Core SSE Hook & Status Indicator
- Implement `useVaultSse` hook in `web/src/features/vault/hooks/use-vault-sse.ts`:
  - Connects to `/api/v1/vault/projects/${projectId}/stream?identity_id=${userId}`.
  - Listens to `connected`, `secret_update`, `ping`, and `error` events.
  - Implements 35s heartbeat watchdog timer.
  - Implements exponential backoff reconnection with jitter (1s base, 10s max cap).
  - Handles page visibility (`visibilitychange`) and clean listener teardown on unmount.
- Implement `LiveSyncStatusBadge` component in `web/src/features/vault/components/live-sync-status-badge.tsx`:
  - Renders green pulsing dot for "Live Sync" (connected).
  - Renders amber dot with spinning icon for "Đang kết nối lại..." (connecting).
  - Renders gray dot for "Ngoại tuyến" (disconnected).
  - Displays tooltip with last ping timestamp and manual "Thử kết nối lại" button.
- Mount `LiveSyncStatusBadge` inside the `VaultView` toolbar.

### Phase 3: User Story 2 (P2) - Auto Cache Invalidation & Seamless Table Hot-Reload
- Inside `useVaultSse`, when `secret_update` arrives:
  - Invalidate TanStack Query caches:
    - `queryClient.invalidateQueries({ queryKey: [...VAULT_KEYS.all, "secrets", projectId] })`
    - `queryClient.invalidateQueries({ queryKey: [...VAULT_KEYS.all, "scopes", projectId] })`
  - Populate `highlightedKeys` state for 2500ms.
- Update `SecretsTable` in `web/src/features/vault/components/secrets-table.tsx`:
  - Add optional `highlightedKeys?: Set<string>` prop.
  - When a row's key is in `highlightedKeys`, apply a smooth transient blue highlight ring/glow (`ring-2 ring-blue-500/50 bg-blue-50/40 transition-all duration-700`).

### Phase 4: User Story 3 (P3) - Live Audit Feed & Notification Toasts
- In `useVaultSse`, when `secret_update` arrives:
  - Push event into in-memory `events` array (capped at 20 latest events).
  - Trigger Sonner toast: `toast.info("${actor} vừa cập nhật biến ${keys} (Scope: ${scope})", { duration: 4000 })`.
- Implement `LiveAuditFeed` component in `web/src/features/vault/components/live-audit-feed.tsx`:
  - Triggered by a "Nhật ký Live" button with event counter badge.
  - Renders a clean popover or sheet showing recent change events with relative timestamps ("vừa xong", "1 phút trước"), scope badge, actor, and version.
  - Allows pausing/resuming live synchronization stream.
- Wire `LiveAuditFeed` into `VaultView`.

### Phase 5: Verification & Polish
- Full typecheck: `pnpm --prefix web typecheck` (0 errors).
- Full production build: `pnpm --prefix web build` (successful compilation).
- Backend test validation: `uv run pytest` (46/46 passed).
- Dual-window live test from `quickstart.md`.
