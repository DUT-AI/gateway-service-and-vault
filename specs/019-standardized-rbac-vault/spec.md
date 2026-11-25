# Feature Specification: Standardized 3-Tier Role-Based Access Control & Vault ACL

**Feature Branch**: `019-standardized-rbac-vault`

**Created**: 2026-11-25

**Status**: Draft

**Input**: User description: "Tôi muốn xây dựng lại hệ thống phân quyền cho chỉnh chu, chứ ko chấp vá như bây giờ, Hiện tại chỉ có 3 role bạn cần quan tâm: role_names: ['admin', 'Trainer', 'Project Developer', 'Content'], là Project Developer, admin, còn lại là những role còn lại á"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - System Administrator Complete Governance (Priority: P1) 🎯 MVP

As a System Administrator (`admin`), I need comprehensive visibility and control over all Gateway resources (Projects, Services, Quotas, Keys, Audit) and Dynamic Vault secrets across all scopes, so that I can govern the entire platform without manual header hacks or arbitrary permission blocks.

**Why this priority**: Core administrative foundation. Administrators must have uninhibited, audited access to manage infrastructure, configure services, and grant/revoke access to team members.

**Independent Test**: Log in with an SSO account having the `admin` role. Navigate through all projects, view/decrypt all secrets under all scopes, modify quotas, and grant/revoke key-level permissions to other users without providing manual override headers.

**Acceptance Scenarios**:

1. **Given** an authenticated user with `admin` in `role_names`, **When** accessing any project workspace, **Then** all secret scopes and decrypted secret values are visible without requiring explicit rows in the `key_permissions` table.
2. **Given** an administrator, **When** accessing the "Phân quyền truy cập" (Key Permission Matrix) modal, **Then** the administrator can view permissions for any user in the directory and grant or revoke access to any secret key.
3. **Given** an administrator, **When** managing Gateway resources (creating projects, binding upstream services, setting rate limits and daily quotas), **Then** all operations succeed with 200/201 HTTP status.
4. **Given** an administrator listening to the real-time SSE stream (`/vault/projects/{id}/stream`), **Then** all secret rotation events are received in real time regardless of key name.

---

### User Story 2 - Project Developer Workspace & Secret Management (Priority: P2)

As a `Project Developer`, I need to work within project environments, manage service configurations, create environment secrets, and access keys permitted to me, so that I can develop and deploy applications without compromising production secrets.

**Why this priority**: Developers are the primary daily users of the platform. They need frictionless access to create and manage secrets while respecting least-privilege boundaries.

**Independent Test**: Log in as a `Project Developer`. Create a new secret `PAYMENT_API_KEY`. Verify the secret is saved and immediately visible to the creator. Verify that sensitive secrets not granted to this developer are masked or omitted. Verify attempts to alter global gateway quotas or delete projects are rejected with HTTP 403 Forbidden.

**Acceptance Scenarios**:

1. **Given** a user with `Project Developer` role, **When** creating a new environment secret in an assigned project, **Then** the secret is encrypted with AES-256-GCM, persisted, and immediately accessible.
2. **Given** an assigned project containing secrets across multiple scopes, **When** a `Project Developer` views the Vault tab or calls `GET /api/v1/vault/projects/{id}/secrets`, **Then** the developer can read **all decrypted secrets** in that assigned project (key-level ACL applies to machine clients/SDKs and restricted roles).
3. **Given** a `Project Developer`, **When** listing projects or attempting to access a project workspace, **Then** the system strictly restricts visibility and access to **assigned projects only** (via Project Membership); accessing an unassigned project returns HTTP 403 Forbidden.
4. **Given** a `Project Developer`, **When** attempting administrative operations (e.g., deleting projects, updating global gateway service definitions, or assigning project members), **Then** the system returns HTTP 403 Forbidden with an explicit authorization denial error.

---

### User Story 3 - Project-Scoped & Key-Filtered Access for Other Roles (Trainer, Content, etc.) (Priority: P3)

As an organization member with non-developer roles (such as `Trainer`, `Content`, or default member), I should only see projects I am assigned to, view details of those projects, and view/manage only the secrets I personally created or were explicitly assigned to me via key-level permissions.

**Why this priority**: Enforces Zero-Trust least privilege while allowing cross-functional team members (Trainers, Content creators) to collaborate safely within their assigned projects without exposing unrelated infrastructure secrets.

**Independent Test**: Log in as a user with role `Trainer` or `Content` who is a member of Project A (and not Project B). Verify Project A appears in their project list and Project B does not. Create a secret in Project A and verify it is visible; verify secrets created by others are hidden unless explicitly granted in `key_permissions`.

**Acceptance Scenarios**:

1. **Given** a user with only `Trainer` or `Content` in `role_names`, **When** viewing the Dashboard / Project Hub, **Then** only projects they are assigned to via Project Membership are listed, and they can enter the detail view of those assigned projects.
2. **Given** an assigned project, **When** a user with `Other Roles` views the Vault tab or calls `GET /api/v1/vault/projects/{id}/secrets`, **Then** the system returns **only secrets created by them OR secrets explicitly granted to their identity in `key_permissions`**, hiding all other keys.
3. **Given** an assigned project, **When** a user with `Other Roles` creates a secret, **Then** the system persists the secret and automatically grants them key permission so they can read/update it.
4. **Given** a user with `Other Roles`, **When** attempting to access an unassigned project, manage project members, create virtual keys/mTLS certificates, or modify gateway quotas, **Then** the backend returns HTTP 403 Forbidden and administrative UI controls are hidden.

---

### Edge Cases

- **Multiple Roles in Token**: If a user's SSO token contains multiple roles (e.g., `["Trainer", "Project Developer", "admin"]`), the system MUST evaluate privileges based on the highest role tier (`admin` > `Project Developer` > `Other Roles`).
- **Unassigned / Unknown Role**: If an authenticated user has an empty role list or unmapped roles, the system MUST default them to the lowest privilege tier ("Other Roles").
- **Expired or Revoked Token**: If the SSO token is revoked or expired on DUT-AI Manage IdP, the system MUST fail closed immediately and return HTTP 401 Unauthorized across all endpoints.
- **Direct Parameter Tampering**: If a `Project Developer` attempts to bypass UI restrictions by injecting `X-Identity-Id: admin` or `X-User-Role: admin` headers into HTTP requests, the backend MUST ignore user-supplied identity headers and strictly honor the cryptographically verified SSO token claims.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST define and enforce a strict 3-tier Role-Based Access Control (RBAC) hierarchy derived directly from SSO token claims (`role_names` and `role`):
  1. **Tier 1: `admin`** (Full System & Project Administration)
  2. **Tier 2: `Project Developer`** (Project-level development & permitted secrets)
  3. **Tier 3: `Other Roles`** (Restricted viewers including `Trainer`, `Content`, and unmapped roles).
- **FR-002**: The backend authentication layer MUST extract caller identity and roles exclusively from verified DUT-AI SSO tokens (`Authorization: Bearer` or `access_token` cookie) via `IExternalUserDirectoryService` / `/api/v1/auth/me`. Client-supplied spoofing headers (`X-Identity-Id`, `X-User-Role`) MUST NOT override authenticated token claims in production.
- **FR-003**: For `admin` users, the system MUST automatically bypass key-level ACL filtering, granting unrestricted read/write access to all secret scopes and management endpoints.
- **FR-004**: The system MUST support Project Membership (`project_members`) binding SSO User IDs to Projects. `admin` users can view/access all projects and manage project memberships; `Project Developer` and `Other Roles` users MUST only view and access projects they are explicitly assigned to.
- **FR-005**: For `Project Developer` users, the system MUST allow reading **all** decrypted secrets and creating/updating secrets within their assigned projects, as well as managing virtual keys and mTLS client certificates for those assigned projects.
- **FR-006**: For `Other Roles` (`Trainer`, `Content`, etc.), within their assigned projects, the system MUST allow viewing project details, creating secrets (with automatic key permission granted to the creator), and reading **only** secrets they created or secrets explicitly granted to them in `key_permissions`. Administrative mutations (virtual keys, quotas, permissions matrix, project deletion) MUST return HTTP 403 Forbidden.
- **FR-007**: The frontend UI MUST dynamically adjust navigation, project lists, and action buttons ("Thêm biến mới", "Phân quyền truy cập", "Tích hợp SDK", "Cấu hình Quota", "Quản lý thành viên") according to the active user's resolved role tier.
- **FR-008**: The Server-Sent Events (SSE) stream (`/vault/projects/{id}/stream`) MUST strictly filter secret rotation broadcasts according to the resolved role tier: `admin` and `Project Developer` (on assigned projects) receive all project events; `Other Roles` and machine clients only receive events for keys they hold explicit permission to read.

### Key Entities

- **User Identity (SSO)**: Authenticated identity verified against DUT-AI Manage IdP with attributes: `id` (integer), `email`, `name`, `role` (primary role string), `role_names` (list of assigned role strings), `permissions` (list of feature flags).
- **Role Tier**: Computed authorization classification:
  - `ADMIN`: User has `admin` in `role_names` or wildcard `*` in `permissions`.
  - `PROJECT_DEVELOPER`: User has `Project Developer` in `role_names` (and is not `ADMIN`).
  - `OTHER_ROLES`: Any user with roles not meeting the above tiers (e.g. `Trainer`, `Content`).
- **Project Membership**: Binding between `project_id` and `user_id` (integer from SSO), determining which projects a non-admin user (`Project Developer` or `Other Roles`) can access.
- **Key Permission**: Granular mapping between a `project_id`, `identity_id` (user ID or client ID), and a specific `secret_key`, recording `granted_by` and timestamps.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of API endpoints enforce role-based access control without relying on manual HTTP header overrides or hardcoded developer IDs.
- **SC-002**: An `admin` user can view, edit, and rotate any secret in any project with 0 permission denial errors.
- **SC-003**: When a `Project Developer` creates a secret, it is immediately visible and manageable by that developer with zero latency or manual permission grant required.
- **SC-004**: Users with `Trainer` or `Content` roles cannot view decrypted secret values or execute mutating operations across 100% of tested attack vectors (UI and direct REST API).
- **SC-005**: Real-time SSE secret update events are dispatched to connected clients in under 2 seconds while achieving 100% precision in key-level permission filtering.

## Assumptions

- User role assignments are managed authoritatively by the central DUT-AI Manage Identity Provider (`https://manage.dutai.io.vn`) and are propagated via SSO tokens.
- The 3-tier hierarchy satisfies all business needs for the current operational phase; additional custom roles will map into one of these 3 tiers.
- Key-level ACL (`key_permissions` table) continues to serve as the granular mechanism for non-admin identities.
