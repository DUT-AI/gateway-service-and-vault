# Feature Specification: Core Security & Gateway Enforcement (Phase 1)

**Feature Branch**: `013-gateway-security-enforcement`

**Created**: 2026-11-23

**Status**: Draft

**Input**: User description: "/speckit-specify hãy implement Giai đoạn 1: Thực thi Bảo mật Cốt lõi & Gateway Enforcement (Ưu tiên P1 - Critical)"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - APISIX Runtime Identity Binding & mTLS Enforcement (Priority: P1)

As a System Administrator and Security Auditor, I want Apache APISIX to strictly enforce mTLS and validate the cryptographic identity binding (`X-Virtual-Key` + client certificate fingerprint) on every upstream request before forwarding to backend services, so that any unauthenticated connection or stolen API key is blocked immediately at the gateway ingress.

**Why this priority**:
Core Principle VIII and Customer Requirement 1.2 mandate Zero-Trust machine-level binding. Currently, upstream service routes in APISIX only execute URL rewrites; without runtime Lua filter enforcement, external clients can bypass hardware certificate verification and call upstream endpoints directly.

**Independent Test**:
1. Deploy APISIX with mounted `identity-binding-filter` Lua plugin.
2. Send an HTTP request to `http://localhost:9080/services/llm/models` without `X-Virtual-Key` or mTLS -> Verify Gateway immediately responds with `HTTP 401 Unauthorized` or `HTTP 403 Forbidden`.
3. Send a request with valid mTLS certificate + valid Virtual Access Key -> Verify Gateway successfully verifies binding, strips the virtual key, injects upstream credentials, and forwards to the upstream service with `HTTP 200 OK`.

**Acceptance Scenarios**:
1. **Given** a client calling `/services/{slug}/*` without providing `X-Virtual-Key`, **When** APISIX receives the request, **Then** APISIX rejects with `HTTP 401 Unauthorized` (`UNAUTHORIZED`).
2. **Given** a client calling `/services/{slug}/*` over plain HTTP or without presenting a valid mTLS client certificate, **When** APISIX processes the request, **Then** APISIX rejects with `HTTP 403 Forbidden` (`MTLS_REQUIRED`).
3. **Given** a client presenting a valid client certificate and a valid `X-Virtual-Key` bound to `(Client, Project)`, **When** APISIX queries `/api/v1/gateway/verify-binding`, **Then** the binding is confirmed, `X-Virtual-Key` is stripped, upstream credentials are injected, and the upstream response is returned.

---

### User Story 2 - Service Scoping Enforcement at Gateway Ingress (Priority: P1)

As a Project Administrator, I want the APISIX Gateway filter to extract the target service slug from the requested URI and check whether the calling Project is authorized to consume this specific service, so that applications belonging to Project A cannot invoke services restricted to Project B.

**Why this priority**:
Requirement FR-10 and Customer Requirement "Đúng dự án, đúng dịch vụ" dictate that projects can only access approved upstream APIs. Even with a valid mTLS certificate and key, unauthorized cross-service calls must be denied at the Gateway.

**Independent Test**:
1. Ensure Project A has Service X in its allowlist, but Service Y is excluded.
2. Use Client A's certificate and Project A's Virtual Key to call `/services/x/...` -> Returns `HTTP 200 OK`.
3. Use the same credentials to call `/services/y/...` -> Gateway rejects with `HTTP 403 Forbidden` (`ServiceNotPermittedError`).

**Acceptance Scenarios**:
1. **Given** a client authenticated with valid key and certificate for Project A, **When** the client calls an upstream route `/services/{slug}/*` where `{slug}` is permitted for Project A, **Then** the request is forwarded successfully.
2. **Given** a client authenticated with valid key and certificate for Project A, **When** the client calls `/services/{slug}/*` where `{slug}` is NOT permitted for Project A, **Then** the Gateway returns `HTTP 403 Forbidden` indicating the service is not allowed for this project.

---

### User Story 3 - Hardware/Device Identity Revocation (Revoke Client) (Priority: P1)

As a System Administrator, when a developer's laptop is reported lost/stolen or an employee departs the organization, I want to revoke the registered client device from the Control Plane API, so that the hardware identity is invalidated and all Virtual Access Keys assigned to that device are revoked in a single atomic operation.

**Why this priority**:
Section 3.1 & 3.3 of `mo_ta.md` states: "Thu hồi thiết bị sẽ vô hiệu hóa toàn bộ chứng chỉ và Virtual Key liên quan." Currently, the system only allows revoking individual virtual keys; revoking a compromised client device itself is missing.

**Independent Test**:
1. Register a client device and generate an active Virtual Access Key.
2. Verify that `POST /api/v1/gateway/verify-binding` succeeds.
3. Call `POST /api/v1/gateway/clients/{client_id}/revoke`.
4. Verify that the client's `is_revoked` flag is `true` and all associated virtual keys are transitioned to `REVOKED`.
5. Call `verify-binding` with the previously valid credentials -> Verify rejection with `HTTP 403 Forbidden` ("Client is not found or revoked").

**Acceptance Scenarios**:
1. **Given** an active Registered Client with one or more active Virtual Access Keys, **When** the administrator issues a revocation request to `POST /api/v1/gateway/clients/{id}/revoke`, **Then** the client record is marked `is_revoked = true` and all active keys for that client are atomically set to `REVOKED`.
2. **Given** a revoked client device, **When** any request arrives at the Gateway with a certificate or key linked to that client, **Then** the Gateway rejects the request with `HTTP 403 Forbidden`.
3. **Given** an already revoked client or non-existent client ID, **When** a revocation request is sent, **Then** the endpoint returns `HTTP 404 Not Found` or `HTTP 400 Bad Request`.

---

### User Story 4 - Visual Client Revocation & State Management on Web UI (Priority: P2)

As an Administrator browsing the Web UI, I want to see a clear "Thu hồi thiết bị" (Revoke Client) action on the Clients table with a confirmation modal, and have revoked devices clearly flagged with a red `REVOKED` badge, so that I can safely manage hardware lifecycles without accidental revocations.

**Why this priority**:
Provides human-in-the-loop operational safety for zero-trust lifecycle management.

**Independent Test**:
1. Navigate to `/clients` in the web application.
2. Click "Thu hồi thiết bị" on an active client row.
3. Confirm the warning dialog stating all virtual keys for this device will be revoked.
4. Verify the row updates immediately with a red `REVOKED` badge and the revocation button is disabled or hidden.

**Acceptance Scenarios**:
1. **Given** an active client in the Clients table, **When** the user clicks "Thu hồi thiết bị", **Then** a confirmation dialog appears explaining the consequences (all active keys will be invalidated).
2. **Given** the confirmation dialog is confirmed, **When** the mutation succeeds, **Then** the table row reflects the `REVOKED` state and displays a success toast.
3. **Given** a client that is already revoked, **When** viewing the table, **Then** the action button is disabled and the badge clearly displays "Đã thu hồi" (Revoked).

---

### Edge Cases

- **Control Plane Offline or Slow (Fail-Closed Policy)**: When APISIX cannot reach `http://api:8000/api/v1/gateway/verify-binding` within the 2-second timeout window, the Lua filter MUST fail closed and return `HTTP 503 Service Unavailable` or `HTTP 403 Forbidden`, never allowing requests through unverified.
- **Plaintext HTTP Traffic**: If a client calls `/services/*` over port 9080 without TLS termination, `ngx.var.ssl_client_fingerprint` is nil/empty; the Lua filter immediately aborts with `HTTP 403 Forbidden` (`MTLS_REQUIRED`).
- **Concurrent Revocation Requests**: Calling revoke on an already revoked client must be idempotent and handle potential race conditions gracefully without corrupting database state.
- **Service Slug Resolution**: If an upstream route is requested with trailing subpaths (e.g. `/services/llm/v1/chat/completions`), the Lua regex must accurately capture `llm` as the service slug regardless of query parameters or nested path depth.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Docker Compose and APISIX configuration MUST mount `./apps/apisix/plugins` to `/usr/local/apisix/plugins:ro` and register `identity-binding-filter` in `apps/apisix/conf/config.yaml`.
- **FR-002**: The Lua plugin `identity-binding-filter.lua` MUST parse the `service_slug` from `ngx.var.uri` and include it in the JSON verification payload sent to the Control Plane.
- **FR-003**: The APISIX route generator in `modules/gateway/client/apisix_client.py` MUST automatically include `identity-binding-filter` in the route plugins whenever an upstream service route is created or synchronized.
- **FR-004**: `POST /api/v1/gateway/verify-binding` and `VerifyIdentityBindingUseCase` MUST support resolving `service_slug` to verify service permissions against `project_allowed_services`.
- **FR-005**: Backend domain layer MUST define `revoke_client(client_id: str)` in `IRegisteredClientRepository` and implement `RevokeClientUseCase` to revoke both the client and all associated active virtual keys in a single transaction.
- **FR-006**: Backend API MUST expose `POST /api/v1/gateway/clients/{client_id}/revoke` protected by authentication and validation.
- **FR-007**: Web Frontend client service (`client-service.ts`) and hooks (`use-clients-queries.ts`) MUST provide `revokeClient` mutations and handle cache invalidation for `['registered-clients']` and `['virtual-keys']`.
- **FR-008**: Web Frontend `ClientsTable` MUST render a confirmation modal and action button for device revocation, with disabled states and badge styling for revoked devices.

---

### Key Entities *(include if feature involves data)*

- **RegisteredClient**: Represents an enrolled user laptop (`USER_DEVICE`) or Docker deployment (`APP_SERVER`). Key attributes: `id`, `name`, `client_type`, `cert_fingerprint`, `is_revoked`, `created_at`.
- **VirtualAccessKey**: Virtual token bound to `(RegisteredClient, Project)`. Status transitions from `ACTIVE` to `REVOKED` when the associated `RegisteredClient` is revoked.
- **ProjectAllowedService**: Relationship joining `Project` and `UpstreamService`, checked by `VerifyIdentityBindingUseCase` on each request forwarded through APISIX.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of unauthenticated or non-mTLS requests to `/services/*` are rejected by APISIX with `HTTP 401` or `HTTP 403` in under 5ms.
- **SC-002**: Legitimate mTLS requests with valid bound Virtual Keys pass identity verification and upstream credential injection with Gateway overhead under 15ms at p95.
- **SC-003**: Revoking a client device via the API or Web UI takes effect immediately (within 1 database transaction), instantly blocking subsequent requests from that certificate and all of its virtual keys.
- **SC-004**: 100% of automated unit and integration tests for identity binding, service scoping, and client revocation pass without regression.

---

## Assumptions

- APISIX runs in the same Docker network (`boilerplate-net`) as the FastAPI backend (`api:8000`) and has network connectivity to `http://api:8000/api/v1/gateway/verify-binding`.
- The internal CA root certificate is trusted by APISIX for mTLS client certificate validation on port 9443.
- When a client is revoked, the operation is irreversible; generating new credentials requires registering a new client entity.
