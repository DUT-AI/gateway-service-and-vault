# Phase 0: Research & Technical Decisions - Real-Time Dynamic Vault Hot-Reload

**Feature**: `004-vault-hot-reload`  
**Date**: 2026-11-23  
**Status**: Completed  

---

## 1. Streaming Protocol: Server-Sent Events (SSE) vs. WebSocket vs. Long-Polling

### Context
Client applications require real-time notifications (< 1 second) whenever a secret configuration changes on the Control Plane so that their in-memory configurations can be rotated without process restarts.

### Decision
Use **HTTP Server-Sent Events (SSE)** (`text/event-stream`) over HTTP/1.1 or HTTP/2.

### Rationale
- **Unidirectional Semantics**: Configuration streaming is strictly server-to-client push. Client applications never need to push secret data back over the stream channel (all secret mutations are handled via standard authenticated REST POST/PUT endpoints).
- **Transport & Firewall Compatibility**: SSE runs on standard HTTP (port 80/443) without protocol upgrade handshakes (`101 Switching Protocols`), traversing enterprise proxies, APISIX API gateway, and load balancers without special tunneling or timeout terminations.
- **Native Reconnection**: SSE protocol specifies automatic reconnect behavior (`retry: 3000`).
- **Resource Footprint**: In FastAPI / Starlette, SSE streams can be implemented efficiently with `StreamingResponse` yielding lines of standard event text or via `sse-starlette`, maintaining open connections with minimal memory overhead (< 4KB per connection buffer).
- **Comparison to Alternatives**:
  - *WebSockets*: Bidirectional complexity, custom ping/pong framing, firewall/proxy impedance mismatches, and unnecessary duplex state management for read-only notifications.
  - *Long-Polling*: High HTTP handshake and connection teardown overhead, latency jitter (averaging 500ms-2s latency penalty), and excessive database/Redis query pressure.

---

## 2. Event Broker: Redis Pub/Sub vs. Kafka / RabbitMQ vs. PostgreSQL LISTEN/NOTIFY

### Context
When a secret is created, updated, or revoked in `modules/vault`, all active SSE streaming instances across multiple API gateway or backend worker replicas must immediately receive the event and fan out notifications to subscribed client SDK connections.

### Decision
Use **Redis Pub/Sub** on channel pattern `vault:project:{project_id}:changes`.

### Rationale
- **Existing Infrastructure**: Redis (`redis:7-alpine`) is already part of the project container topology and configured in `core/config/redis.py` and `docker-compose.yml`.
- **Ultra-Low Latency**: In-memory pub/sub message propagation latency is typically under 1 millisecond.
- **Ephemeral Fan-out**: Configuration update notifications are ephemeral trigger signals telling clients: "Key X in Scope Y has changed; re-fetch your authorized state". Clients do not need long-term stream persistence or replay from the pub/sub broker because:
  - If a client disconnects and reconnects, it immediately fetches the current state via REST GET `/api/v1/vault/projects/{project_id}/secrets`.
  - Redis Pub/Sub does not accumulate stale messages in memory, preventing memory leaks when no subscribers are present.
- **Alternatives Considered**:
  - *Kafka / RabbitMQ*: Heavyweight infrastructure with excess operational burden and resource overhead for small notification payloads.
  - *PostgreSQL LISTEN/NOTIFY*: Coupled with database connection limits; scaling SSE connections would consume scarce PostgreSQL backend process connections.

---

## 3. Client-Side In-Memory Ingestion & Hot-Reload (`dut-vault-sdk`)

### Context
Developers and container runtimes must eliminate plaintext `.env` files entirely on disk while supporting zero-downtime updates to in-memory configuration variables within 5 seconds.

### Decision
Implement `dut-vault-sdk` (Python SDK and CLI runner) with:
1. **Thread-Safe In-Memory Store (`InMemoryConfigStore`)**:
   - Internal dictionary protected by an reentrant lock (`threading.RLock`).
   - Mutations update the dictionary atomically and optionally inject into `os.environ` in-place.
2. **Background Async/Thread Listener**:
   - Spawns a lightweight daemon thread running an event loop or `httpx` streaming client.
   - Listens to `GET /api/v1/vault/projects/{project_id}/stream`.
   - On receiving `secret_update` event:
     - Calls `GET /api/v1/vault/projects/{project_id}/secrets?scope={scope}` with client credentials.
     - Decrypts and merges changed keys into the in-memory store.
     - Executes registered `on_change(key, callback)` lifecycle hooks asynchronously.
3. **Zero-Disk Invariant Enforcement**:
   - The SDK never touches `open(..., 'w')`, never creates temporary files, and never uses disk-based caching.
   - CLI execution (`dut-vault run -- ...`) sets environment variables directly in the spawned child process's RAM.
4. **Resilience & Reconnection**:
   - Exponential backoff with randomized jitter (starting at 1.0s up to max 30.0s).
   - Heartbeat watchdog: If no message or ping is received within 45 seconds (server sends pings every 15s), the stream is considered broken, cleanly torn down, and re-established.

---

## 4. Clean Architecture & Modular Monolith Compliance

### Context
The project strictly enforces Clean Architecture purity (Constitution Principle I) and Dishka IoC (Principle II).

### Decision
- **Domain Layer (`modules/vault/domain/`)**:
  - Define `ConfigChangeEvent` as a pure Python dataclass in `modules/vault/domain/entities.py`.
  - Define `IVaultBroadcaster` protocol interface in `modules/vault/domain/interfaces.py`.
  - Zero imports of FastAPI, Pydantic, or SQLAlchemy in domain files.
- **Infrastructure Layer (`modules/vault/infrastructure/` or `modules/vault/services/`)**:
  - Implement `RedisVaultBroadcaster(IVaultBroadcaster)` utilizing `redis.asyncio.Redis`.
  - Provide broadcaster via Dishka `VaultProvider` with `Scope.APP`.
- **Application Layer (`modules/vault/use_cases/`)**:
  - `CreateSecretUseCase` injects `IVaultBroadcaster` and dispatches `ConfigChangeEvent` upon committing secret updates.
- **Presentation Layer (`apps/api/routers/vault_router.py`)**:
  - Expose `GET /api/v1/vault/projects/{project_id}/stream` using FastAPI `StreamingResponse`.
  - Authenticate client credentials and subscribe to Redis channel `vault:project:{project_id}:changes`.
