# Data Model: Web Phase 3 - Real-Time Vault Hot-Reload Stream (SSE Live Sync)

**Feature**: `009-web-vault-sse-sync`  
**Date**: 2026-11-23  

## 1. Stream Event Interfaces

These types model the Server-Sent Events transmitted by the backend `GET /api/v1/vault/projects/{project_id}/stream` endpoint.

```typescript
export type SseConnectionStatus =
  | "connected"
  | "connecting"
  | "disconnected"
  | "error";

/**
 * Emitted immediately upon successful connection establishment.
 * Event name: "connected"
 */
export interface SseConnectedEvent {
  project_id: string;
  status: "active";
  timestamp: string; // ISO 8601
}

/**
 * Emitted when a secret is created, updated, or rotated.
 * Event name: "secret_update"
 */
export interface SseSecretUpdateEvent {
  event_id: string; // UUID
  project_id: string;
  scope_name: string;
  changed_keys: string[];
  new_version: number;
  actor: string; // User ID or email
  timestamp: string; // ISO 8601
}

/**
 * Heartbeat emitted every 15 seconds to keep connection alive.
 * Event name: "ping"
 */
export interface SsePingEvent {
  timestamp: string; // ISO 8601
}

export type VaultStreamEvent =
  | { type: "connected"; data: SseConnectedEvent }
  | { type: "secret_update"; data: SseSecretUpdateEvent }
  | { type: "ping"; data: SsePingEvent };
```

---

## 2. Live Sync Client State Model

```typescript
export interface VaultSseState {
  status: SseConnectionStatus;
  lastPing: Date | null;
  events: SseSecretUpdateEvent[];
  isPaused: boolean;
  highlightedKeys: Set<string>;
  reconnect: () => void;
  togglePause: () => void;
  clearHistory: () => void;
}
```

---

## 3. Connection State Machine

```
               ┌───────────────────────┐
               │     DISCONNECTED      │
               └──────────┬────────────┘
                          │ (Mount / Reconnect trigger)
                          ▼
               ┌───────────────────────┐
        ┌─────>│      CONNECTING       │<────┐
        │      └──────────┬────────────┘     │
        │                 │ (event: connected)│
        │                 ▼                  │
        │      ┌───────────────────────┐     │ (Connection drop /
        │      │       CONNECTED       │─────┘  Heartbeat timeout)
        │      └──────────┬────────────┘
        │                 │ (Fatal error)
        │                 ▼
        │      ┌───────────────────────┐
        └──────│         ERROR         │
               └───────────────────────┘
```

- **Transitions**:
  - `disconnected` $\rightarrow$ `connecting`: When `useVaultSse` mounts or `reconnect()` is invoked.
  - `connecting` $\rightarrow$ `connected`: When the initial `event: connected` packet arrives.
  - `connected` $\rightarrow$ `connecting`: When network drops or no ping/message is received for > 35s.
  - `connected` $\rightarrow$ `error`: When server returns non-200 HTTP code (e.g. 403 Forbidden).
  - Any state $\rightarrow$ `disconnected`: When component unmounts.
