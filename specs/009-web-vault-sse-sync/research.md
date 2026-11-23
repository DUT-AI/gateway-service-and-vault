# Research: Web Phase 3 - Real-Time Vault Hot-Reload Stream (SSE Live Sync)

**Feature**: `009-web-vault-sse-sync`  
**Date**: 2026-11-23  

## 1. SSE Client Transport & Authentication

### Decision
Use a resilient SSE connection manager supporting both standard browser `EventSource` with query credentials (`/api/v1/vault/projects/${projectId}/stream?identity_id=${userId}`) and optional `fetch`-based `ReadableStream` for environments requiring explicit `Authorization: Bearer` token headers.

### Rationale
- **Zero Third-Party Bloat**: Built directly on native browser web APIs (`EventSource` / `fetch` + `ReadableStreamDefaultReader`) without pulling heavy external dependencies.
- **Cross-Origin & Cookie Support**: `withCredentials: true` transmits the `access_token` session cookie automatically on same-origin and proxy-routed configurations.
- **Backend Harmony**: Adding an optional `identity_id: str | None = Query(default=None)` parameter to `apps/api/routers/vault/stream.py` allows seamless identification of the user while preserving backwards compatibility with existing HTTP header tests (`x_identity_id`).

### Alternatives Considered
- *WebSockets (`ws://` / `wss://`)*: Overkill for unidirectional server-to-client configuration broadcasts. SSE is simpler, operates over standard HTTP/1.1 and HTTP/2, traverses corporate proxies and firewalls without custom port handling, and has native streaming response support in FastAPI (`StreamingResponse`).
- *Short Polling (every 2s)*: Excessive server load, high Redis query volume, wasteful bandwidth, and does not achieve < 3s latency without overwhelming the server.

---

## 2. Reconnection Algorithm & Heartbeat Watchdog

### Decision
Implement a two-tier resilience strategy:
1. **Heartbeat Watchdog**: The backend emits `event: ping` every 15 seconds. If no message (event or ping) is received within 35 seconds, the client assumes a dead/silent connection and proactively closes and restarts the connection.
2. **Exponential Backoff with Full Jitter**:
   $$\text{delay} = \min\left(1000 \times 2^{\text{attempt}} + \text{random}(0, 500), 10000\right)\text{ ms}$$
   Resets backoff attempt counter to 0 upon receiving `event: connected`.

### Rationale
- Prevents infinite connection loops and stampeding herd problems when the backend or Redis restarts.
- Handles mobile device sleep, laptop lid closures, and Wi-Fi handoffs gracefully.

---

## 3. Real-Time Cache Invalidation & Row Highlighting

### Decision
When `event: secret_update` arrives:
1. Extract `changed_keys: string[]`, `scope_name: string`, and `actor: string`.
2. Dispatch TanStack Query cache invalidation:
   ```typescript
   queryClient.invalidateQueries({ queryKey: VAULT_KEYS.secrets(projectId) });
   queryClient.invalidateQueries({ queryKey: VAULT_KEYS.scopes(projectId) });
   ```
3. Add `changed_keys` to an ephemeral React state set `highlightedKeys` for 2500ms.
4. Pass `highlightedKeys` to `SecretsTable` to render an animated highlight ring (`ring-2 ring-blue-500/50 bg-blue-50/40 transition-all duration-500`).
5. Emit a Sonner notification toast: *"Admin vừa cập nhật biến [KEYS] (Scope: [SCOPE])"*.

### Rationale
- Provides immediate visual feedback indicating exactly which row was modified without disorienting the user.
- Maintains user search input, pagination, and scroll state without jarring refreshes.
