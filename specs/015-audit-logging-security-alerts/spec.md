# Feature Specification: Audit Logging & Security Alerts System (Phase 3)

**Feature Branch**: `015-audit-logging-security-alerts`  
**Created**: 2026-11-23  
**Status**: Ready for Planning  
**Input**: Giai đoạn 3: Hệ Thống Nhật Ký Kiểm Toán & Cảnh Báo An Ninh (Ưu tiên P2 - High)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Immutable Audit Logging for Gateway Access Decisions (Priority: P1)

As a Security Officer or System Administrator, I want the system to automatically and immutably record every security decision made by the Gateway verification layer, distinguishing between User Device and App Server actors, recording allowed access and detailed denial causes (such as Identity Mismatch, Revoked Key, Expired Key, Service Not Allowed, or Daily Quota Exceeded), so that we have complete visibility and non-repudiation into who accessed which service and which requests were rejected.

**Why this priority**: Core requirement FR-12 and security compliance demand immutable audit logging for all access decisions. Without this, security incidents and unauthorized attempts cannot be investigated or proven.

**Independent Test**:
Call the Gateway verification use case (`VerifyIdentityBindingUseCase`) with both valid credentials and invalid/mismatched credentials; query the `audit_events` repository and verify that corresponding `ALLOW` and `DENY` records are persisted with correct actor, decision, client_type, and error_code.

**Acceptance Scenarios**:
1. **Given** a valid Virtual Key and matching client certificate for an allowed service, **When** `VerifyIdentityBindingUseCase` executes, **Then** an audit event is persisted with `action="GATEWAY_ACCESS"`, `decision="ALLOW"`, `client_type` matching the registered client, and `error_code=None`.
2. **Given** a Virtual Key presented with a mismatched certificate fingerprint, **When** `VerifyIdentityBindingUseCase` executes and raises `IdentityMismatchError`, **Then** an audit event is persisted with `action="GATEWAY_ACCESS"`, `decision="DENY"`, and `error_code="IDENTITY_MISMATCH"`.
3. **Given** a Virtual Key exceeding daily quota, **When** `VerifyIdentityBindingUseCase` raises `DailyQuotaExceededError`, **Then** an audit event is persisted with `action="GATEWAY_ACCESS"`, `decision="DENY"`, and `error_code="DAILY_QUOTA_EXCEEDED"`.

---

### User Story 2 - Audit Log Query & Security Anomaly Detection API (Priority: P2)

As a Tech Lead or Security Auditor, I want a secure REST API to search, filter, and paginate through historical audit events by project, client type (`USER_DEVICE` vs `APP_SERVER`), decision (`ALLOW` vs `DENY`), action, and time range, as well as an endpoint to retrieve active security alerts (e.g. repeated Identity Mismatches indicating potential token theft or machine cloning), so that I can monitor platform security and inspect anomalies programmatically.

**Why this priority**: Auditing data stored in the database is useless without efficient, secure query capabilities and anomaly detection for rapid incident response.

**Independent Test**:
Seed audit events with multiple projects, dates, and denial reasons; call `GET /api/v1/gateway/audit-events` with various query filter combinations; verify correct filtering, pagination metadata (`total`, `limit`, `offset`), and call `GET /api/v1/gateway/security-alerts` to verify anomaly detection.

**Acceptance Scenarios**:
1. **Given** audit events in the system, **When** requesting `GET /api/v1/gateway/audit-events?project_id={id}&decision=DENY`, **Then** only `DENY` events belonging to that project are returned with pagination metadata.
2. **Given** more than 3 `IDENTITY_MISMATCH` events occurred within a 5-minute sliding window from the same actor or client IP, **When** requesting `GET /api/v1/gateway/security-alerts`, **Then** a security alert item is returned with severity `HIGH`, anomaly type `REPEATED_IDENTITY_MISMATCH`, and count details.

---

### User Story 3 - Web UI "Nhật Ký An Ninh & Cảnh Báo" (Audit Logs View) (Priority: P2)

As a Workspace Administrator or Security Auditor using the Web UI, I want a dedicated "Nhật ký an ninh" page accessible from the sidebar navigation featuring a filterable audit logs table and a security alert banner, so that I can easily inspect access histories, view actor details, and immediately spot red security violations.

**Why this priority**: Human operators require a clear, intuitive dashboard to monitor security posture without needing direct database access or CLI scripts.

**Independent Test**:
Navigate to `/audit` on the Web UI; verify sidebar link "Nhật ký an ninh" is active; verify table displays timestamp, actor badge (`User Device` vs `App Server`), project, service, action, status badge (`ALLOW` green vs `DENY` red), and filter controls work seamlessly.

**Acceptance Scenarios**:
1. **Given** an authenticated user on the Web UI, **When** clicking "Nhật ký an ninh" in the sidebar, **Then** the `/audit` page renders with the audit logs table and filter controls.
2. **Given** filter selections (e.g. Decision = DENY), **When** applying the filter, **Then** the table updates to show only matching events.
3. **Given** active security alerts exist, **When** viewing the page, **Then** an alert banner is displayed at the top highlighting the security anomaly in red/amber.

---

### Edge Cases

- **Database Transient Failure**: When logging an audit event, a database timeout or transient error MUST NOT crash the gateway verification if fail-open audit policy is active, or must be safely isolated so downstream upstream traffic is protected.
- **Unbound or Unknown Virtual Key**: When a client presents an entirely unrecognized Virtual Key, `project_id` and `actor_id` may be unknown; the system must log `actor_id="UNKNOWN"` and `project_id="UNKNOWN"` with `client_ip` and raw key prefix in metadata.
- **High-Volume Audit Event Ingestion**: Large volume of requests must not degrade gateway latency; DB insert operations must use indexed timestamps and efficient queries.
- **Pagination Boundary**: Offsets exceeding total count return empty items list with accurate total count without crashing.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an immutable `IAuditEventRepository` interface in `modules/gateway/domain/interfaces.py` and SQLAlchemy implementation `SqlAuditEventRepository` in `modules/gateway/repository/audit_repository.py`.
- **FR-002**: `VerifyIdentityBindingUseCase` MUST record an audit event for every verification attempt:
  - On success: `action="GATEWAY_ACCESS"`, `decision="ALLOW"`, `client_type` of client, `actor_id=client.id`, `project_id=...`, `service_id=...`.
  - On failure: `action="GATEWAY_ACCESS"`, `decision="DENY"`, with `error_code` capturing the failure reason (`IDENTITY_MISMATCH`, `DAILY_QUOTA_EXCEEDED`, `CLIENT_REVOKED`, `INVALID_KEY`, `SERVICE_NOT_ALLOWED`).
- **FR-003**: System MUST expose `GET /api/v1/gateway/audit-events` supporting:
  - Pagination parameters: `limit: int = 50`, `offset: int = 0`.
  - Filter parameters: `project_id: str | None`, `client_type: str | None`, `decision: str | None`, `action: str | None`, `date_from: datetime | None`, `date_to: datetime | None`, `error_code: str | None`.
- **FR-004**: System MUST expose `GET /api/v1/gateway/security-alerts` returning detected security anomalies:
  - Detection rule: Multiple `IDENTITY_MISMATCH` events (threshold >= 3 within 5 minutes) grouped by actor/fingerprint/IP.
- **FR-005**: Web UI MUST include "Nhật ký an ninh" in the main navigation sidebar (`web/src/components/layout/app-shell.tsx`) pointing to `/audit`.
- **FR-006**: Web UI MUST provide an Audit Logs page (`web/src/app/(protected)/audit/page.tsx`) with:
  - Search and filter bar (Decision, Client Type, Project, Date range).
  - Data table with formatted timestamp, actor type badges (`User Device` vs `App Server`), decision badges (`ALLOW` emerald vs `DENY` rose), error code, and expandable metadata viewer.
  - Security Alert banner alerting operators when anomalies are detected.

### Key Entities

- **AuditEventEntity**: Core immutable domain entity representing an access decision or security event:
  - `id: str` (ULID)
  - `timestamp: datetime` (UTC)
  - `client_type: ClientType` (`USER_DEVICE` or `APP_SERVER`)
  - `actor_id: str`
  - `project_id: str`
  - `service_id: str | None`
  - `action: str`
  - `decision: str` (`ALLOW`, `DENY`)
  - `client_ip: str | None`
  - `error_code: str | None`
  - `metadata: dict`
- **SecurityAlert**: Domain/DTO representation of an active security anomaly:
  - `alert_id: str`
  - `severity: str` (`HIGH`, `MEDIUM`, `LOW`)
  - `anomaly_type: str` (`REPEATED_IDENTITY_MISMATCH`, `UNUSUAL_VOLUME`)
  - `description: str`
  - `actor_id: str | None`
  - `client_ip: str | None`
  - `event_count: int`
  - `first_seen_at: datetime`
  - `last_seen_at: datetime`

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Gateway access requests (both approved and rejected) produce an immutable audit log record in `audit_events`.
- **SC-002**: Audit event queries with any combination of filters execute with indexed scan response time under 100ms for 100,000+ records.
- **SC-003**: 3 consecutive `IDENTITY_MISMATCH` requests trigger an active `HIGH` severity alert returned by `GET /api/v1/gateway/security-alerts` within 1 second.
- **SC-004**: Frontend `/audit` page renders with full type safety (`make api-types` and `pnpm tsc --noEmit` pass with 0 errors).
- **SC-005**: 100% test pass rate across backend pytest suite, integration tests, and live E2E tests.
