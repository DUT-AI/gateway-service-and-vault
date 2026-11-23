# Feature Specification: Gateway Real-Time Quota & Rate Limiting Enforcement (Phase 2)

**Feature Branch**: `014-gateway-quota-rate-limiting`
**Created**: 2026-11-23
**Status**: Specified
**Input**: User request for Phase 2: Thực thi Quota & Rate Limit thực tế tại Gateway (P2 - High)

---

## Executive Summary
This feature implements real-time traffic shaping, rate limiting, and daily quota enforcement for all API calls traversing Apache APISIX to upstream backend services. While previous features stored `rate_limit_rpm` and `quota_daily` in the database, this feature activates live enforcement at the gateway and control plane layers:
1. **Per-Minute Rate Limiting**: Apache APISIX `limit-count` plugin throttles incoming requests per Virtual Key based on the route's configured `rate_limit_rpm` (returning `HTTP 429 Too Many Requests`).
2. **Daily Quota Enforcement**: An atomic Redis counter (`INCR`) tracks daily request volume per `(project_id, service_id)` pair, rejecting requests once `quota_daily` is reached.
3. **Usage Inspection API & UI**: Administrators and Tech Leads can view real-time daily usage metrics and percentage progress bars on the Web UI.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Live Gateway Rate Limiting per Route (Priority: P1) 🎯 MVP

As an API platform administrator, I want APISIX to automatically throttle rapid bursts of requests exceeding the configured Requests-Per-Minute (`rate_limit_rpm`) threshold, so that upstream services are shielded from denial-of-service or sudden traffic spikes.

**Why this priority**: Without rate limiting, compromised keys or runaway client loops can overwhelm upstream providers (e.g. LLM APIs) and exhaust credits or degrade service stability.

**Independent Test**:
- Send rapid sequential requests using cURL / test script exceeding the route's `rate_limit_rpm` (e.g. > 5 req/min in a test window).
- Verify APISIX responds with `HTTP 429 Too Many Requests` containing standard rate limit headers.

**Acceptance Scenarios**:
1. **Given** an upstream service route configured with `rate_limit_rpm = 60`, **When** a client sends fewer than 60 requests in a 60-second window, **Then** all requests are forwarded to upstream and return `HTTP 200 OK`.
2. **Given** an upstream service route configured with `rate_limit_rpm = 5` for testing, **When** a client sends the 6th request within 60 seconds, **Then** APISIX immediately rejects the request with `HTTP 429 Too Many Requests` without dispatching to the control plane or upstream service.

---

### User Story 2 - Daily Quota Tracking via Redis Atomic Counter (Priority: P1)

As an organization Tech Lead, I want a daily ceiling (`quota_daily`) enforced per Project and Service, so that individual projects do not exceed their allocated operational budget.

**Why this priority**: Daily quotas prevent budget overruns on costly external APIs (e.g. commercial LLMs, translation services).

**Independent Test**:
- Set a project service binding with `quota_daily = 3`.
- Make 3 successful calls through the gateway.
- On the 4th call, verify the gateway verification rejects the request with `HTTP 429` and error message `DAILY_QUOTA_EXCEEDED`.

**Acceptance Scenarios**:
1. **Given** a valid project-service quota policy with `quota_daily = 1000`, **When** a valid request arrives at `/api/v1/gateway/verify-binding`, **Then** the control plane atomically increments `gateway:quota:{project_id}:{service_id}:{date}` in Redis with 24-hour TTL.
2. **Given** the Redis counter has reached or exceeded `quota_daily`, **When** another request is processed, **Then** the control plane raises `QuotaExceededError` and returns `HTTP 429 Too Many Requests`.
3. **Given** the clock rolls over to the next day (UTC midnight), **Then** a new Redis counter key is used and usage resets to 0.

---

### User Story 3 - Real-Time Quota Usage Inspection API (Priority: P2)

As a Tech Lead or Developer, I want to query the current day's usage statistics for any service bound to my project, so that I can monitor consumption and anticipate quota limits.

**Why this priority**: Transparency in resource consumption enables proactive quota adjustment and troubleshooting.

**Independent Test**:
- Call `GET /api/v1/gateway/projects/{project_id}/services/{service_id}/usage`.
- Verify the response returns `usage_today`, `quota_daily`, `rate_limit_rpm`, and `usage_percentage`.

**Acceptance Scenarios**:
1. **Given** an active project-service binding with 150 calls recorded today and a quota of 1000, **When** calling `GET /api/v1/gateway/projects/{project_id}/services/{service_id}/usage`, **Then** the API returns `{"usage_today": 150, "quota_daily": 1000, "rate_limit_rpm": 60, "usage_percentage": 15.0}`.
2. **Given** no calls have been made today, **When** calling the usage endpoint, **Then** the API returns `usage_today: 0` and `usage_percentage: 0.0`.

---

### User Story 4 - Visual Quota Usage Progress Bar on Web UI (Priority: P2)

As a project manager viewing the Allowed Services table on `/projects/{id}`, I want to see a visual progress bar indicating daily quota consumption for each service, so that I can assess project health at a glance.

**Why this priority**: Visual feedback prevents unexpected quota lockouts and makes resource management intuitive.

**Independent Test**:
- Navigate to `/projects/{id}` in the browser.
- Verify each service row in the "Dịch vụ được phép" table shows a progress bar with formatted text (e.g. `1,250 / 10,000 requests (12.5%)`).
- Verify color coding: green (<80%), yellow (80-99%), red (≥100%).

**Acceptance Scenarios**:
1. **Given** a service with 25% usage, **When** viewing the table, **Then** the progress bar renders in emerald/green.
2. **Given** a service with 85% usage, **When** viewing the table, **Then** the progress bar renders in amber/yellow.
3. **Given** a service with 100% usage, **When** viewing the table, **Then** the progress bar renders in rose/red with a "Hết hạn mức" badge.

---

## Edge Cases & Defensive Invariants
1. **Redis Temporary Outage (Fail-Open vs Fail-Closed)**: If Redis is temporarily unreachable during quota increment, the system MUST log a high-priority warning and fail open (allow the request) rather than breaking production availability, while recording an alert.
2. **Timezone Uniformity**: Daily keys MUST strictly use UTC dates (`YYYYMMDD`) to prevent inconsistencies across distributed servers.
3. **Concurrent Increment Race Conditions**: Redis `INCR` is natively atomic in single-threaded command execution, guaranteeing zero lost counts during concurrent bursts.
4. **Rate Limit Headers**: APISIX `limit-count` automatically adds `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` headers to downstream responses.
