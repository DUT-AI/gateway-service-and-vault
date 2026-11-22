# Feature Specification: Secure API Gateway & Centralized Dynamic Vault Platform

**Feature Branch**: `003-api-gateway-vault`

**Created**: 2026-11-23

**Status**: Draft

**Input**: User description: "Thiết kế và triển khai nền tảng Gateway Service & Vault: Xác thực mTLS bắt buộc, ràng buộc Identity Binding (Virtual Access Key = Client + Project), che giấu upstream credentials, phân vùng Service Scope & Rate Limit/Quota, quản lý biến môi trường/bí mật tập trung theo vai trò (Least Privilege, xóa bỏ file .env thủ công), đồng bộ cấu hình thời gian thực nạp thẳng vào RAM (In-Memory Hot-Reload), tích hợp SSO DUT AI Manage, đảm bảo Fail-Closed."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Client Identity & Key Binding Enforcement at API Gateway (Priority: P1)

As a Security Administrator, I need the API Gateway to enforce cryptographic client identity (mTLS) and strictly bind Virtual Access Keys to the specific registered client device/workload and authorized project, so that stolen or shared keys cannot be replayed from unauthorized machines or cross-used across projects.

**Why this priority**: Preventing key leakage, credential sharing, and unauthorized API consumption is the foundational zero-trust security gate of the entire platform.

**Independent Test**: Deploy two simulated clients (Client A and Client B). Client A calls an API endpoint using its valid certificate and bound Virtual Access Key, successfully receiving responses. Client B attempts to use Client A's key (or Client A uses its key on an unauthorized project); the Gateway terminates connection or immediately rejects with HTTP 403 Forbidden.

**Acceptance Scenarios**:

1. **Given** Client A has a valid mTLS certificate and a Virtual Access Key bound to `(Client A, Project X)`, **When** Client A sends a request to an upstream service via the Gateway, **Then** the Gateway successfully verifies the TLS handshake, matches the certificate identity with the Virtual Access Key, injects upstream credentials, forwards the request, and records an allowed audit event.
2. **Given** Client B has a valid mTLS certificate but presents a Virtual Access Key bound to Client A (or Client A presents a key bound to Project Y while requesting Project X), **When** Client B calls the Gateway, **Then** the Gateway detects identity mismatch, rejects the request with HTTP 403 Forbidden, emits a high-severity security alert, and logs the violation.
3. **Given** an external actor without a trusted mTLS certificate attempts to call the Gateway with a stolen Virtual Access Key, **When** initiating connection, **Then** the Gateway terminates the connection at the TLS handshake level before reaching application routing.

---

### User Story 2 - Role-Based Centralized Secret Management without Plaintext Files (Priority: P2)

As a Developer or Team Lead, I need to retrieve project configurations and secrets dynamically based on my authenticated identity and assigned role from DUT AI Manage, so that sensitive credentials are never distributed via chat/email or stored as plaintext `.env` files on developer disks.

**Why this priority**: Eliminates sensitive credential leakage on local workstations and enforces the principle of least privilege across different engineering disciplines (e.g., General Frontend vs. Core Finance).

**Independent Test**: Authenticate as a Financial Developer and a General Frontend Developer via DUT AI Manage SSO. Verify the Financial Developer receives payment secrets and common variables, while the General Developer only receives common variables and receives access-denied for financial scopes.

**Acceptance Scenarios**:

1. **Given** a Developer with the "Financial" role successfully logs in via DUT AI Manage SSO, **When** requesting project secrets, **Then** the Control Plane delivers both Common and Financial configuration scopes.
2. **Given** a Developer with the "General/Frontend" role logs in via DUT AI Manage SSO, **When** requesting project secrets, **Then** the Control Plane delivers Common variables and strictly omits or rejects access to Financial or Core system scopes.
3. **Given** an unauthenticated request or expired SSO session, **When** requesting secrets, **Then** the Control Plane returns HTTP 401 Unauthorized and logs the unauthorized attempt.

---

### User Story 3 - Real-Time In-Memory SDK Secret Hot-Reloading (Priority: P3)

As an Application Operator or Developer, I need the application runtime to dynamically ingest and update configuration secrets directly in process memory (RAM) in real time when changed in the Control Plane, without saving files to disk or requiring application restarts.

**Why this priority**: Prevents configuration drift and eliminates service downtime caused by manual updates or rolling restarts when credentials rotate.

**Independent Test**: Start an application process integrated with the client SDK. Modify a configuration variable in the Control Plane. Verify the application process reflects the updated value in RAM within 5 seconds without restarting the process and without any file being written to the filesystem.

**Acceptance Scenarios**:

1. **Given** a running application workload initialized with the SDK, **When** an Administrator updates or revokes a secret in the Control Plane, **Then** the Control Plane pushes the update event to connected SDK clients within 5 seconds.
2. **Given** the SDK receives a secret update notification, **When** applying the change, **Then** the SDK updates the in-memory configuration store immediately, keeping the process running and leaving zero temporary or plaintext files on disk.

---

### User Story 4 - Service Scoping Allowlist & Atomic Quota Enforcement (Priority: P4)

As a Project Lead or Platform Admin, I need to restrict which upstream API services each project can call and enforce atomic request limits (Rate Limiting & Quota), so that compromised or misconfigured applications cannot call unauthorized APIs or exhaust external service budgets.

**Why this priority**: Prevents noisy-neighbor starvation, enforces departmental budget limits, and isolates blast radius if a project key is abused.

**Independent Test**: Configure Project A with access only to Service X and Service Y with a limit of 10 requests/minute. Send requests from Project A to Service Z (verify HTTP 403) and send 11 requests to Service X (verify HTTP 429 on the 11th request).

**Acceptance Scenarios**:

1. **Given** Project A is only granted access to Service X and Service Y, **When** a client of Project A calls Service Z, **Then** the Gateway blocks the request with HTTP 403 Forbidden with a service-not-permitted reason.
2. **Given** Project A has exceeded its allocated request limit (RPM/RPH/daily quota), **When** subsequent requests are sent, **Then** the Gateway responds with HTTP 429 Too Many Requests and includes a `Retry-After` header.

---

### Edge Cases

- **Control Plane Outage (Fail-Closed):** If the API Gateway or SDK loses connection to the Control Plane, the Gateway strictly enforces a Fail-Closed policy by rejecting incoming requests (HTTP 503) rather than allowing unverified traffic. New application processes cannot start in an offline or unverified state.
- **Revoked or Expired mTLS Certificate:** Even if presenting a valid Virtual Access Key, connections with revoked or expired client certificates are rejected at the TLS handshake.
- **Deactivated User in DUT AI Manage:** When an employee account is disabled in DUT AI Manage, all associated Device Identities and active SDK sessions are revoked immediately upon the next token verification cycle.
- **High-Concurrency Rate Burst:** Rate limit counters must operate atomically across multiple gateway instances to prevent limit circumvention under concurrent load.
- **Container Lifecycle Rotation:** Docker container restarts or scale-out events must utilize service-level machine identity credentials, preventing identity breakage across ephemeral container recreation.

## Requirements *(mandatory)*

### Functional Requirements

#### Domain 1: Client Identity & Gateway Access Control
- **FR-001**: System MUST require mutual TLS (mTLS) for all incoming connections from Registered Clients (User Devices and Docker App Servers), terminating connections during the TLS handshake for invalid certificates.
- **FR-002**: System MUST bind each Virtual Access Key exclusively to a single `(Registered Client, Project)` pair, enforcing that at most one active key exists per pair at any given time.
- **FR-003**: System MUST verify that the client identity extracted from the mTLS certificate matches the bound owner of the Virtual Access Key on every HTTP request.
- **FR-004**: System MUST reject any mismatched or cross-used Virtual Access Key with HTTP 403 Forbidden and trigger high-severity audit alerts.
- **FR-005**: System MUST conceal upstream credentials from clients, automatically injecting upstream authentication tokens (API Keys, Bearer tokens, or Basic Auth headers) at the Gateway proxy layer.

#### Domain 2: Centralized Secrets & Role-Based Access Control
- **FR-006**: System MUST organize configuration secrets by Project and Scopes (e.g., `Common`, `Financial`, `Auth-Core`, `Frontend`).
- **FR-007**: System MUST enforce Role-Based Access Control (RBAC) mapped to DUT AI Manage user roles, allowing developers to read only secrets within authorized scopes.
- **FR-008**: System MUST authenticate all administrative and developer actions exclusively through the central DUT AI Manage Identity Provider via OIDC/OAuth2.

#### Domain 3: Dynamic In-Memory SDK Synchronization
- **FR-009**: System MUST provide an application SDK capable of injecting configurations directly into process RAM without writing `.env` or plaintext files to the local disk.
- **FR-010**: System MUST propagate secret modifications, additions, and revocations from the Control Plane to running SDK instances in real time (< 5 seconds) without application restarts.

#### Domain 4: Service Scoping & Quota Control
- **FR-011**: System MUST enforce a per-project API Service Allowlist, rejecting calls to unauthorized upstream service names with HTTP 403 Forbidden.
- **FR-012**: System MUST track and enforce atomic request rate limits and usage quotas (RPM, RPH, daily quotas) per `(Project, Registered Client, Upstream API Service)`, returning HTTP 429 Too Many Requests when thresholds are breached.

#### Domain 5: Auditing & Operational Safety
- **FR-013**: System MUST generate immutable audit logs for all security-relevant events (successful calls, identity mismatches, secret access, rate limit rejections, and administrative policy changes) labeled by client type (`User Device` vs. `App Server`).
- **FR-014**: System MUST strictly adhere to a Fail-Closed posture: if the Control Plane is unreachable, the Gateway rejects unverified incoming requests and developer environments cannot boot unverified secrets.
- **FR-015**: System MUST never log plaintext values of secrets, upstream credentials, or raw sensitive payloads.

### Key Entities

- **Project**: Represents a business initiative or product boundary; owns allowed upstream services and configuration scopes.
- **Registered Client**: Cryptographically identified client entity; either a `User Device` (associated with a specific human user) or an `App Server` (associated with a Docker service workload).
- **Virtual Access Key**: An ephemeral or rotating virtual credential mapped 1:1 to a specific `(Registered Client, Project)` pair.
- **Secret / Config Item**: An encrypted key-value pair belonging to a specific Scope within a Project, maintaining version history and audit trails.
- **Scope**: Logical grouping of secrets (e.g., `Common`, `Financial`) mapped to RBAC permissions.
- **Upstream API Service**: Target external or internal API destination definition (routing path, upstream URL, encrypted real credential, allowed projects).
- **Quota & Rate Limit Policy**: Rule specifying allowable request velocity (RPM/RPH/daily) per project and client.
- **Audit Event**: An immutable timestamped log record capturing actor, client type, action, resource, decision (Allow/Deny), and metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of unauthorized key replay attempts (using a key on a different device or different project) are detected and blocked at the Gateway.
- **SC-002**: Zero plaintext `.env` files or secret disk artifacts are generated across developer workstations and application container environments.
- **SC-003**: In-memory secret hot-reload updates are reflected in client applications within 5 seconds of an administrative change.
- **SC-004**: Gateway authentication and identity binding validation introduces less than 20ms of latency overhead at the 95th percentile (p95).
- **SC-005**: 100% of developer and administrative access is authenticated through DUT AI Manage single sign-on.
- **SC-006**: Rate limit checks maintain atomic precision under concurrent loads of at least 1,000 requests per second per gateway node without counter undercounting or over-allocation.

## Assumptions

- Developers possess workstations capable of generating or storing standard x509 TLS client certificates.
- Target Docker environments have volume/secret mounting capabilities to supply machine certificates for `App Server` workloads.
- The DUT AI Manage IdP service (`https://manage.dutai.io.vn`) provides stable OIDC endpoints and accessible user metadata (roles and permissions).
- Brief service downtime during intentional key rotation is acceptable under the Single Active Key policy.
- Fail-Closed security takes precedence over continuous offline availability.
