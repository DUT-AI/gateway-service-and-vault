# Research & Design Decisions: Project Upstream Service Binding & Quota Governance

**Feature Branch**: `012-project-service-binding`
**Created**: 2026-11-23

## Technical Context Research

### 1. Project-to-Upstream Service Association & Relational Persistence

- **Context**: In Phase 5, `UpstreamServiceModel` was established. The database schema in `modules/gateway/models/project.py` already defines:
  ```python
  project_upstream_association = Table(
      "project_upstream_allowlist",
      Base.metadata,
      Column("project_id", String(26), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
      Column("service_id", String(26), ForeignKey("upstream_services.id", ondelete="CASCADE"), primary_key=True),
  )
  ```
- **Decision**: Reuse `project_upstream_allowlist` as the authoritative persistence table for project-service bindings.
- **Rationale**: The table already features composite primary keys (`project_id`, `service_id`) with cascading foreign keys to both `projects` and `upstream_services`, eliminating orphan records automatically when either entity is deleted.
- **Alternatives Considered**:
  - *Storing allowed services as a JSON array on `ProjectModel`*: Rejected because it prevents relational foreign key constraints, disables database-level indexing, and makes reverse lookups (finding which projects use a service) inefficient.

---

### 2. Quota Policy Storage & Composite Mapping

- **Context**: `QuotaPolicyModel` is defined in `modules/gateway/models/quota.py` with columns `project_id`, `service_id`, `client_id`, `rate_limit_rpm` (default 60), `quota_daily` (default 10000), `is_active` (boolean).
- **Decision**: When an upstream service is bound to a project:
  1. Insert a row into `project_upstream_allowlist` (`project_id`, `service_id`).
  2. Create or upsert a `QuotaPolicyModel` record for (`project_id`, `service_id`, `client_id=None`) with specified `rate_limit_rpm` and `quota_daily`.
- **Rationale**: Setting `client_id=None` represents the default project-wide quota for that upstream service. If future phases introduce device-specific quota overrides, the schema accommodates it without schema changes.
- **Alternatives Considered**:
  - *Storing quota columns directly on the join table*: Rejected because `quota_policies` is already designed and partitioned to support client-level granularity and active/inactive toggles.

---

### 3. Clean Architecture & Domain Separation

- **Context**: In accordance with Principle I (Clean Architecture) and Principle II (Modular Monolith with Dishka):
  - Domain entities in `modules/gateway/domain/entities.py` must remain pure dataclasses.
  - Use cases in `modules/gateway/use_cases/` encapsulate all business validation and transaction orchestration.
  - Repositories in `modules/gateway/repository/` implement SQL queries using SQLAlchemy 2.0 `asyncpg`.
  - Dependency injection is wired cleanly via `modules/gateway/di.py`.
- **Decision**: Implement domain-level methods in `IProjectRepository` (or dedicated `IProjectServiceBindingRepository`):
  - `list_allowed_services_with_quota(project_id: str) -> list[ProjectAllowedServiceDTO]`
  - `bind_service_to_project(project_id: str, service_id: str, rate_limit_rpm: int, quota_daily: int)`
  - `unbind_service_from_project(project_id: str, service_id: str)`
  - `update_service_quota(project_id: str, service_id: str, rate_limit_rpm: int, quota_daily: int)`
- **Rationale**: Keeps repository calls explicit and testable while ensuring Dishka container manages database session lifetime cleanly.

---

### 4. REST API Endpoint Design

- **Endpoints**:
  - `GET /api/v1/gateway/projects/{project_id}/services`: Returns list of bound services with service info (id, name, slug, base_url, auth_type) and quota policy (rate_limit_rpm, quota_daily, is_active).
  - `POST /api/v1/gateway/projects/{project_id}/services`: Binds an upstream service to the project with quota parameters (`service_id`, `rate_limit_rpm`, `quota_daily`). Returns HTTP 201 Created.
  - `PUT /api/v1/gateway/projects/{project_id}/services/{service_id}/quota`: Updates quota parameters for an existing binding. Returns HTTP 200 OK.
  - `DELETE /api/v1/gateway/projects/{project_id}/services/{service_id}`: Unbinds the service and removes its quota policy. Returns HTTP 204 No Content.
- **Error Handling**:
  - `404 Not Found`: If project or service does not exist.
  - `409 Conflict`: If attempting to bind a service that is already bound to the project.
  - `422 Unprocessable Entity`: If `rate_limit_rpm` <= 0 or `quota_daily` <= 0.

---

### 5. Frontend UX & Tab Navigation

- **Context**: In `web/src/features/projects/components/project-workspace-tabs.tsx`, tabs currently exist for:
  - `vault`: Environment variables (Dynamic Vault)
  - `keys`: Virtual Keys (Machine/Device credentials)
  - `settings`: Project metadata
- **Decision**: Add a new tab `services` titled `"Dịch vụ liên kết"` with an icon (e.g. `Server` or `Globe` or `Layers`).
  - View component: `ProjectAllowedServicesView` (`web/src/features/projects/components/project-allowed-services-view.tsx`).
  - Sub-components:
    - `AllowedServicesTable`: Table displaying bound services, endpoint badges, auth type, RPM rate limit, daily quota, and unbind/edit actions.
    - `BindServiceDialog`: Dialog containing a searchable select dropdown of available catalog services (filtering out already-bound services), number inputs for RPM (default 60) and Daily Quota (default 10,000), and a submit button with loading state.
    - `UnbindConfirmDialog`: Accessible confirmation dialog warning the user before revoking service access.
- **Rationale**: Matches the visual design system of the existing tabs (MUI v7/Tailwind CSS v4 with Radix UI primitives), ensuring high discoverability and zero friction.

---

### 6. Zero-Trust Gateway Validation Hook

- **Context**: When incoming requests are authenticated in APISIX or simulated via `VerifyIdentityBindingUseCase`:
  - `VerifyIdentityBindingUseCase` currently validates client cert fingerprint and virtual key hash.
  - If a `service_id` or `service_slug` is provided in the verification request, verify that `service_id` is present in the project's `project_upstream_allowlist`.
  - If not in allowlist, return `decision="DENY"` with `error_code="SERVICE_NOT_PERMITTED_FOR_PROJECT"`.
- **Rationale**: Implements Principle VIII (Zero-Trust Identity Binding) end-to-end.
