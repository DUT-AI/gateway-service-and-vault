# Research & Architectural Decisions: Audit Logging & Security Alerts (Phase 3)

**Branch**: `015-audit-logging-security-alerts` | **Date**: 2026-11-23

## 1. Storage & Persistence: Direct DB Insert vs Transactional Outbox vs Redis Buffer

### Context
Gateway access verification (`VerifyIdentityBindingUseCase`) evaluates every request routed through APISIX. Each verification yields either an `ALLOW` decision or a `DENY` decision with an error code (`IDENTITY_MISMATCH`, `DAILY_QUOTA_EXCEEDED`, `CLIENT_REVOKED`, etc.). We must persist these events immutably.

### Decision
Persist audit events directly to the existing `audit_events` table in PostgreSQL via `SqlAuditEventRepository` asynchronously inside `VerifyIdentityBindingUseCase`.

### Rationale
- The table `audit_events` is already provisioned by migration `002_gateway_and_vault.py` with indexes on `timestamp`, `actor_id`, `project_id`, and `action`.
- A single row insert into PostgreSQL with asyncpg takes ~1-3ms, well within our gateway control-plane latency budget.
- Direct database persistence guarantees immediate read-after-write consistency: a security analyst or automated test querying `/api/v1/gateway/audit-events` immediately sees the event just generated.
- Wrapping the audit insert in an isolated commit ensures that even if the use case raises an HTTP exception (e.g., `IdentityMismatchError` or `DailyQuotaExceededError`), the `DENY` audit record is committed to disk before the error propagates back to APISIX.

### Alternatives Considered
- **Redis Queue / Celery / ARQ Worker**: Adds queue latency and eventual consistency, delaying alert detection and complicating testing.
- **File / Log-based ingestion (e.g. Vector/ELK)**: High operational overhead, not queryable directly by our FastAPI backend without external search service.

---

## 2. Real-Time Anomaly Detection: Database Aggregation vs Redis Sliding Window

### Context
Requirement FR-004 states: "Flag repeated `IDENTITY_MISMATCH` events (> 3 within 5 minutes) as security anomalies."

### Decision
Implement SQL aggregation in `SqlAuditEventRepository.get_security_alerts(window_minutes=5, threshold=3)`.

### Query Architecture
```sql
SELECT
    actor_id,
    client_ip,
    COUNT(*) as mismatch_count,
    MIN(timestamp) as first_seen_at,
    MAX(timestamp) as last_seen_at
FROM audit_events
WHERE action = 'GATEWAY_ACCESS'
  AND error_code = 'IDENTITY_MISMATCH'
  AND timestamp >= :window_start
GROUP BY actor_id, client_ip
HAVING COUNT(*) >= :threshold
ORDER BY mismatch_count DESC;
```

### Rationale
- `timestamp` is indexed, making range queries over the last 5 minutes instantaneous (< 5ms).
- Provides exact timestamps (`first_seen_at`, `last_seen_at`) and exact count.
- Zero state duplication: no need to sync Redis keys or worry about cache expiration desynchronization.
- For high scale in future iterations, a Redis sorted set (`ZADD` with timestamp score) can be placed in front as a caching layer if needed, but SQL aggregation is completely sufficient and robust for the current throughput.

---

## 3. Actor & Client Type Attribution

### Context
Events must clearly distinguish whether the request originated from a `User Device` (developer workstation) or an `App Server` (workload/daemon), as specified in FR-12.

### Decision
Extract `client_type` from `RegisteredClientEntity.client_type` during key verification:
- If key is found and bound to client: `client_type = client.client_type.value` (`USER_DEVICE` or `APP_SERVER`), `actor_id = client.id`, `project_id = key.project_id`.
- If key is missing or invalid: `client_type = "UNKNOWN"`, `actor_id = cert_fingerprint or "ANONYMOUS"`, `project_id = project_id or "UNKNOWN"`.
- If client certificate is absent: record `client_ip` and mark `error_code = "MTLS_REQUIRED"`.

---

## 4. Frontend UI/UX Structure: Dedicated Audit View

### Context
Security auditors and workspace leads need to view logs and alerts conveniently.

### Decision
- Add **"Nhật ký an ninh"** navigation item in `web/src/components/layout/app-shell.tsx` with icon `ShieldAlert` linking to `/audit`.
- Build feature module `web/src/features/audit/`:
  - `services/audit-service.ts`: API client functions `getAuditEvents(params)` and `getSecurityAlerts()`.
  - `hooks/use-audit-queries.ts`: React Query hooks with automatic caching and refetching.
  - `components/audit-logs-table.tsx`: Clean data table with color-coded badges:
    - Actor Type: Purple badge for `APP_SERVER`, Blue badge for `USER_DEVICE`.
    - Decision: Green `ALLOW` badge with `CheckCircle2`, Red `DENY` badge with `XCircle`.
    - Error Code: Rose badge highlighting `IDENTITY_MISMATCH`, `DAILY_QUOTA_EXCEEDED`, etc.
    - JSON Metadata Viewer dialog or popover for full request context.
  - `components/audit-filters-bar.tsx`: Quick filters for Decision, Client Type, Project, Error Code, and Refresh button.
  - `components/security-alerts-banner.tsx`: High-visibility warning alert displayed above the table whenever active alerts exist.
