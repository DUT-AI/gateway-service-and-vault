# Feature Specification: Fail-Closed Hardening & SSO Deactivation Sync (Phase 5)

**Feature Branch**: `017-fail-closed-sso-revocation`  
**Created**: 2026-11-23  
**Status**: Ready for Planning  
**Input**: Giai đoạn 5: Fail-Closed Hardening & Tự Động Thu Hồi Theo SSO (Ưu tiên P4 - Low)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Client & Virtual Key Revocation upon SSO User Deactivation (Priority: P1) 🎯 MVP

As a Security Administrator, when an employee leaves the company or their central account is deactivated / locked on the central DUT-AI Manage SSO IdP, I want all their registered devices (Device Identities) and associated Virtual Access Keys to be automatically and immediately revoked across the Gateway, so that former personnel cannot access any upstream APIs even if they retained valid client certificates on their personal laptops.

**Why this priority**: Eliminates orphaned credentials and access windows when employees depart or roles change.

**Independent Test**:
Given an active client and virtual key owned by SSO user `123`, invoke `POST /api/v1/identity/users/123/sync-revocation` (or webhook); verify the client's `is_revoked` is set to `True`, all active virtual keys are marked `REVOKED`, and subsequent gateway access requests are rejected with `HTTP 403 Forbidden`.

**Acceptance Scenarios**:
1. **Given** a client registered with `owner_id="101"` and active Virtual Keys, **When** invoking sync revocation for user `101`, **Then** the client status becomes `is_revoked = True` and all its keys transition to `REVOKED`.
2. **Given** a revoked client due to SSO account lock, **When** calling `VerifyIdentityBindingUseCase`, **Then** the call fails closed with `IdentityMismatchError` (`CLIENT_REVOKED`).

---

### User Story 2 - Gateway Fail-Closed Hardening & Verification (Priority: P1)

As a Chief Information Security Officer (CISO), I want the API Gateway to strictly fail closed under any Control Plane failure (e.g. Control Plane down, database unreachable, network partitions, or verification timeout), so that under no circumstances can an unauthorized request slip through into upstream services.

**Why this priority**: Core architectural principle of Zero-Trust. A fail-open gateway during an outage would expose upstream LLM and database services to unauthenticated traffic.

**Independent Test**:
Simulate Control Plane timeout or connection refusal in `tests/integration/test_fail_closed.py`; verify that APISIX or the filter returns `HTTP 403 Forbidden` / `HTTP 503 Service Unavailable` with fail-closed error payload and 0 upstream requests reach destination.

**Acceptance Scenarios**:
1. **Given** the Control Plane endpoint is timing out (>2s), **When** a client sends a request through APISIX mTLS, **Then** APISIX terminates the connection with `403 Forbidden` / `503 Service Unavailable` without forwarding to upstream.
2. **Given** an internal 500 error on the Control Plane, **When** verified by APISIX filter, **Then** the request is rejected with `403 Forbidden` (`IDENTITY_MISMATCH` / `CONTROL_PLANE_UNAVAILABLE`).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a use case `SyncSsoUserRevocationUseCase` in `modules/identity/use_cases/sync_sso_user_revocation.py` that, given a `user_id: int`:
  - Queries `IRegisteredClientRepository` for all clients owned by `str(user_id)`.
  - Marks each client as `is_revoked = True`.
  - Revokes all active `VirtualAccessKey` records for those clients.
  - Logs an audit event `action="SSO_USER_REVOKED"`, `decision="ALLOW"`.
- **FR-002**: System MUST expose `POST /api/v1/identity/users/{user_id}/sync-revocation` in `apps/api/routers/auth_router.py` (or `identity_router.py`).
- **FR-003**: In `apps/apisix/plugins/identity-binding-filter.lua`, verify that when `httpc:request_uri` returns `nil` (timeout or connection error) or `res.status >= 500`, the filter immediately terminates with `403 Forbidden` and error code `FAIL_CLOSED`.
- **FR-004**: System MUST provide automated integration test `tests/integration/test_fail_closed.py` validating fail-closed behavior across network errors, timeouts, and SSO user revocation.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of devices and virtual keys belonging to a deactivated SSO user are revoked in under 500ms upon sync trigger.
- **SC-002**: 100% of requests sent during Control Plane unavailability are blocked at ingress (0 requests reach upstream).
- **SC-003**: 100% pass rate in `tests/integration/test_fail_closed.py`.
