# Feature Specification: Project Upstream Service Binding & Quota Governance

**Feature Branch**: `012-project-service-binding`

**Created**: 2026-11-23

**Status**: Draft

**Input**: User description: "Quản lý cấp quyền Dịch vụ Upstream cho Dự án & Thiết lập Hạn mức Quota"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Allowed Upstream Services for a Project (Priority: P1)

As a project administrator, I want to view a comprehensive list of all upstream services authorized for my project inside the Project Workspace, including their service names, target endpoints, authentication methods, and current traffic quota policies (rate limit RPM and daily request cap), so that I understand exactly which APIs my project applications can consume.

**Why this priority**: Visibility is the foundation of access governance. Without seeing which services are bound to a project, administrators cannot audit API permissions, understand consumption limits, or determine whether additional services need to be added.

**Independent Test**: Can be independently tested by navigating to `/projects/{id}` in the web application, selecting the "Dịch vụ liên kết" (Allowed Services) tab, and verifying that all bound services and their quota parameters are accurately displayed in a structured table, or an empty state when no services are bound.

**Acceptance Scenarios**:

1. **Given** a project with one or more bound upstream services, **When** the administrator navigates to the project workspace and opens the "Dịch vụ liên kết" tab, **Then** a table displays each bound service with its name, slug, target endpoint summary, authentication method, rate limit (RPM), daily request limit, active status, and action buttons.
2. **Given** a project with zero bound upstream services, **When** the administrator views the "Dịch vụ liên kết" tab, **Then** an informative empty state is shown explaining that no services are currently permitted for this project, accompanied by a prominent "Thêm dịch vụ" (Add Service) action button.

---

### User Story 2 - Bind Upstream Service to Project with Quota Allocation (Priority: P1)

As a project administrator, I want to authorize an upstream service from the service catalog for my project and configure its traffic quotas (rate limit in requests per minute and daily request limit), so that client applications belonging to this project can securely call the upstream API through the Gateway within defined limits.

**Why this priority**: In a zero-trust model, all upstream access is denied by default. Binding an upstream service to a project is the critical step that permits traffic flow. Without this capability, virtual keys cannot access any protected partner APIs.

**Independent Test**: Can be tested by opening the "Thêm dịch vụ" (Add Service) dialog in the project workspace, selecting an available upstream service, entering quota limits (e.g., 60 RPM, 10,000 requests/day), submitting the form, and confirming that the service immediately appears in the allowed services list.

**Acceptance Scenarios**:

1. **Given** a project and an upstream service catalog containing available services, **When** the administrator clicks "Thêm dịch vụ", selects an unbound service, enters a rate limit (RPM) and a daily quota, and submits, **Then** the service is bound to the project, the quota policy is saved, and the service appears in the project's allowed services list.
2. **Given** an upstream service already bound to the project, **When** the administrator opens the "Thêm dịch vụ" selection list, **Then** the already-bound service is disabled or excluded from selection to prevent duplicate binding.
3. **Given** an administrator entering invalid quota numbers (e.g., negative values, non-numeric characters, or zero), **When** attempting to submit, **Then** validation errors are displayed immediately and submission is prevented.

---

### User Story 3 - Modify Quotas and Revoke Service Access (Priority: P2)

As a project administrator, I want to update traffic quota limits or revoke access to an upstream service when project requirements change or when an integration is decommissioned, so that resource usage remains controlled and access permissions adhere strictly to the principle of least privilege.

**Why this priority**: Long-term maintenance requires adjusting limits as traffic scales and revoking access when APIs are no longer required, preventing stale permissions and accidental overconsumption.

**Independent Test**: Can be tested by clicking "Xóa quyền" (Revoke) on a bound service row, confirming the warning dialog, and observing that the service disappears from the allowed services list. Similarly, editing the quota values updates the displayed limits immediately.

**Acceptance Scenarios**:

1. **Given** a bound upstream service on a project, **When** the administrator clicks "Xóa quyền" (Revoke) and confirms the confirmation prompt, **Then** the service is unlinked from the project and removed from the allowed services list immediately.
2. **Given** an existing bound service with a quota policy, **When** the administrator modifies the rate limit (RPM) or daily request limit and saves, **Then** the updated values are persisted and reflected immediately in the table.

---

### User Story 4 - Zero-Trust Gateway Enforcement of Project Allowlist (Priority: P1)

As a security officer and system operator, I want the API Gateway to strictly enforce the project service allowlist so that incoming requests presenting a valid virtual key are only permitted to reach upstream services explicitly bound to that project, returning HTTP 403 Forbidden for any unauthorized service.

**Why this priority**: This is the core security boundary of the platform. Without automated gateway-level enforcement, allowlists are merely cosmetic and project keys could be abused to access arbitrary internal or third-party APIs.

**Independent Test**: Can be tested by issuing an HTTP request through the gateway with a valid project virtual key targeting a bound service (expect HTTP 200/proxied), and then issuing a request with the same key targeting an unbound service (expect HTTP 403 Forbidden).

**Acceptance Scenarios**:

1. **Given** a client request presenting a valid virtual key for Project A, **When** the request targets an upstream service explicitly bound to Project A within quota limits, **Then** the gateway permits the request, injects real upstream credentials, and proxies to the upstream service.
2. **Given** a client request presenting a valid virtual key for Project A, **When** the request targets an upstream service NOT bound to Project A, **Then** the gateway immediately terminates the request and returns HTTP 403 Forbidden with a clear error payload.
3. **Given** an authorized client request that exceeds the configured rate limit (RPM) or daily request quota for that project-service pair, **When** the request arrives at the gateway, **Then** the gateway returns HTTP 429 Too Many Requests.

---

### Edge Cases

- **Upstream Service Deactivated Globally**: If an upstream service is globally disabled in the catalog, all project-level bindings for that service MUST be treated as inactive by the gateway, rejecting traffic with HTTP 503 or 403 and displaying an "Inactive" status badge in the project workspace.
- **Daily Quota Reset Boundary**: Daily quotas MUST reset automatically at 00:00:00 UTC each day without service interruption or manual intervention.
- **High-Velocity Revocation Propagation**: When an administrator revokes a project's access to a service, in-flight requests that reach the gateway after the revocation transaction MUST be rejected within 5 seconds without requiring gateway restarts.
- **Concurrent Binding Submissions**: If two administrators simultaneously attempt to bind the same upstream service to a project, the system MUST handle the race condition gracefully: exactly one succeeds, and the other receives an informative message that the service is already bound.
- **Service Deletion Safeguard**: If an upstream service is deleted from the global catalog, all associated project bindings and quota policies MUST be cascaded or cleanly decoupled without leaving orphan reference records.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST maintain persistent associations between projects and authorized upstream services.
- **FR-002**: System MUST provide an interface for authorized project administrators to view all upstream services currently bound to a project.
- **FR-003**: System MUST provide an interface for authorized project administrators to bind an available catalog upstream service to a project.
- **FR-004**: System MUST prevent binding an upstream service to the same project more than once.
- **FR-005**: System MUST allow configuring traffic governance limits per project-service pair, including:
  - `rate_limit_rpm`: Maximum requests allowed per minute (positive integer, default 60).
  - `quota_daily`: Maximum requests allowed per calendar day in UTC (positive integer, default 10,000).
- **FR-006**: System MUST allow updating the traffic governance limits (rate limit RPM and daily quota) of an existing project-service binding.
- **FR-007**: System MUST allow revoking/unbinding an upstream service from a project, instantly removing access.
- **FR-008**: The API Gateway MUST enforce project service authorization for every proxied request:
  - Resolve the incoming project identity from the verified virtual access key.
  - Verify that the target upstream service is present in the project's active service allowlist.
  - Fail closed with `HTTP 403 Forbidden` if the service is not in the allowlist.
- **FR-009**: The API Gateway MUST enforce traffic quota policies (rate limit RPM and daily request count) per project-service binding, returning `HTTP 429 Too Many Requests` when limits are exceeded.
- **FR-010**: All service binding additions, quota updates, and access revocations MUST be recorded in an audit trail with timestamp, acting user ID, project ID, and service ID.

### Key Entities

- **Project Service Binding (`project_upstream_allowlist`)**: Represents the authorization link between a Project and an Upstream Service. Key attributes:
  - `project_id`: Unique identifier of the project.
  - `service_id`: Unique identifier of the upstream service.
  - `created_at`: Timestamp when authorization was granted.
- **Quota Policy (`quota_policies`)**: Represents traffic rate and volume limits for a specific project-service binding. Key attributes:
  - `project_id`: Associated project identifier.
  - `service_id`: Associated upstream service identifier.
  - `rate_limit_rpm`: Maximum allowed requests per minute.
  - `quota_daily`: Maximum allowed requests per calendar day (UTC).
  - `is_active`: Boolean flag indicating if policy is active.
  - `updated_at`: Timestamp of latest modification.
- **Upstream Service (Catalog Reference)**: Represents the partner API service registered in the system. Key attributes:
  - `id`: Unique identifier.
  - `name`: Display name (e.g., OpenAI API, VNPay Sandbox).
  - `slug`: URL-friendly identifier.
  - `base_url`: Target destination endpoint.
  - `auth_type`: Credential injection type (`api_key`, `bearer`, `basic`, `none`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Project administrators can complete binding a new upstream service with customized quotas in under 30 seconds.
- **SC-002**: 100% of unauthorized API requests targeting upstream services outside a project's allowlist are rejected at the Gateway layer with HTTP 403 Forbidden.
- **SC-003**: Revoking a service or updating a quota policy takes effect across the Gateway cluster in under 5 seconds.
- **SC-004**: 100% of bound upstream services, their endpoints, and their quota parameters are visible in the Project Workspace without requiring manual page refreshes.
- **SC-005**: Zero duplicate bindings can be created for any project-service pair.

## Assumptions

- Upstream services must be created in the global service catalog before they can be authorized for a project.
- Project administrators have appropriate permissions within their project to manage service bindings.
- All quota calculations and daily limits operate on UTC midnight-to-midnight periods.
- Standard default quota values (60 RPM, 10,000 requests/day) are applied when not explicitly overridden by the administrator.
- Client applications authenticate to the Gateway using project-issued Virtual Keys and mTLS certificates.
