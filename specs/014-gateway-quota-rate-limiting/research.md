# Research: Real-Time Quota & Rate Limiting Enforcement (Phase 2)

## Architectural Decisions

### 1. Rate Limiting Mechanism: APISIX `limit-count` Plugin
- **Decision**: Configure APISIX's native `limit-count` plugin on each dynamic route (`route_{service_slug}`).
- **Rationale**:
  - `limit-count` executes directly inside OpenResty Nginx worker process using a shared memory zone or Redis.
  - It tracks request frequency within a fixed time window (`time_window: 60` seconds).
  - When the count exceeds `count: rate_limit_rpm`, APISIX rejects the request immediately at ingress with `429 Too Many Requests` (`rejected_code: 429`), without invoking the upstream service or control plane.
- **Key Selection**:
  - `key_type: "var"`
  - `key: "http_x_virtual_key"`: Throttles per Virtual Key identity. If absent or empty, falls back to `remote_addr`.
- **Plugin Lifecycle & Header Stripping**:
  - `identity-binding-filter` has priority `2500` (runs early in rewrite phase).
  - `limit-count` has priority `502` (runs later in rewrite phase).
  - In `identity-binding-filter.lua`, we MUST retain `X-Virtual-Key` until after rate limiting runs, OR `limit-count` must run before `X-Virtual-Key` is removed.
  - Solution: In `identity-binding-filter.lua`, we do not strip `X-Virtual-Key` in the `rewrite` phase; instead, we configure APISIX `proxy-rewrite` plugin (`headers: { "remove": ["X-Virtual-Key", "X-Project-Id"] }`) to strip the headers just before sending to upstream!
  - This ensures `limit-count` can access `http_x_virtual_key`, while the upstream never receives the internal virtual key header!

---

### 2. Daily Quota Enforcement: Redis Atomic Counter vs Database
- **Decision**: Use Redis atomic counters (`INCR`) in the Control Plane (`verify-binding` endpoint) with key format `gateway:quota:{project_id}:{service_id}:{YYYYMMDD}`.
- **Rationale**:
  - Database row updates (`UPDATE quota_policies SET used = used + 1`) under high throughput cause row lock contention and database saturation.
  - Redis `INCR` is sub-millisecond (< 0.2ms) and atomic.
  - By including `{YYYYMMDD}` (UTC) in the key, keys rotate automatically at midnight without requiring scheduled midnight cron wipe jobs.
  - Key TTL is set to 172800s (48 hours) to allow review of yesterday's usage while preventing memory accumulation in Redis.
- **Alternatives Considered**:
  - *Database atomic increment*: High DB write contention at 1000+ RPS. Rejected.
  - *Redis sliding window (Sorted Set)*: More complex memory footprint (storing timestamps of each request) when only the daily count is required. Rejected in favor of simple, robust `INCR`.

---

### 3. Fail-Safe Strategy for Redis Availability
- **Decision**: Fail-Open for quota counting if Redis is disconnected.
- **Rationale**:
  - Business availability is prioritized over strict quota counting during infrastructure degradation.
  - If Redis fails, `VerifyIdentityBindingUseCase` catches the connection error, logs an error alert, and permits the call to proceed (rather than returning 500 or 403 to legitimate clients).

---

### 4. Real-Time Usage API & Frontend Display
- **Decision**: Expose `GET /api/v1/gateway/projects/{project_id}/services/{service_id}/usage` and enrich `GET /api/v1/gateway/projects/{project_id}/services` response with current usage stats.
- **Rationale**:
  - Combining current day usage into `ProjectAllowedServiceResponse` allows the frontend `AllowedServicesTable` to render progress bars directly without making N additional HTTP requests for N bound services.
