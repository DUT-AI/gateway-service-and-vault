# Feature Specification: Self-Service mTLS Client & Key UX + Ownership Scoping

**Feature Branch**: `020-mtls-client-ux-scoping`

**Created**: 2026-11-25

**Status**: Draft

**Input**: User description: "Tôi muốn xây dựng là UX của hệ thống trong việc quản lý Quản lý thiết bị & Client mTLS, người dùng dev có thể vào tự tạo, quản lý key cho bản thân mình, admin có thể quản lý các key đang tồn tại trên hệ thống, bạn thấy có vấn đề gì ko ?"

## Clarifications

### Session 2026-11-25

- Q: When an `admin` registers a new mTLS device or server, can they assign ownership (`owner_id`) to another user, or should it always default to the `admin` creating it? → A: Both `admin` and `Project Developer` always register mTLS clients strictly under their own `user_id` (self-issued only; nobody creates certificates/keys on behalf of another user).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Self-Service Device & Key Ownership Isolation (Priority: P1) 🎯 MVP

As a `Project Developer`, I want to register mTLS devices (`USER_DEVICE`) and manage my own Virtual Access Keys without seeing, spoofing, or revoking devices and keys belonging to other users, so that my personal development credentials remain isolated and secure.

**Why this priority**: Currently `GET /clients`, `POST /clients`, `POST /clients/{id}/revoke`, and Virtual Key endpoints lack ownership scoping (`owner_id` check), allowing any Developer to view all users' devices, spoof `owner_id`, and revoke another user's mTLS certificates/keys.

**Independent Test**: Log in as Developer A (`user_id=10`) and register Device A. Log in as Developer B (`user_id=11`). Verify Developer B does NOT see Device A in `GET /clients`, cannot spoof `owner_id="10"` on `POST /clients`, and receives `HTTP 403 Forbidden` if attempting to revoke Device A or generate a key for Device A.

**Acceptance Scenarios**:

1. **Given** a `Project Developer`, **When** listing clients (`GET /api/v1/gateway/clients`), **Then** the system returns **only** clients where `owner_id == str(current_user.user_id)`.
2. **Given** a `Project Developer`, **When** registering a new mTLS client (`POST /api/v1/gateway/clients`), **Then** the backend strictly sets `owner_id = str(current_user.user_id)` from the verified SSO token, ignoring any client-supplied `owner_id`.
3. **Given** a `Project Developer`, **When** attempting to revoke a client (`POST /clients/{id}/revoke`) bound to a client they do not own, **Then** the backend returns `HTTP 403 Forbidden`.
4. **Given** a `Project Developer`, **When** registering a client, **Then** they are permitted to register both `USER_DEVICE` and `APP_SERVER` client types, with ownership (`owner_id`) automatically locked to their own SSO user ID.

---

### User Story 2 - System Administrator System-Wide Client & Key Governance (Priority: P2)

As a System Administrator (`admin`), I want full visibility and governance over all mTLS devices, workload servers (`APP_SERVER`), and Virtual Access Keys across the entire system, with clear owner identity display (name, email, avatar) and filtering, so that I can audit, onboard servers, and revoke compromised keys at any time.

**Why this priority**: Administrators must be able to oversee all machine identities and revoke compromised devices/keys across any owner or project.

**Independent Test**: Log in as `admin`. Navigate to "Thiết bị & Client". Verify all clients across all owners are visible with resolved SSO user names/avatars, filterable by owner/type/status, and Admin can revoke any client or create `APP_SERVER` workload certificates.

**Acceptance Scenarios**:

1. **Given** an `admin` user, **When** viewing "Thiết bị & Client" (`GET /api/v1/gateway/clients`), **Then** all registered clients across all owners are returned, enriched or displayed with SSO owner profile details (name, email, avatar) instead of raw numeric IDs.
2. **Given** an `admin` user, **When** revoking any client or virtual key in the system, **Then** the operation succeeds (`200 OK`) regardless of `owner_id`.
3. **Given** an `admin` or `Project Developer`, **When** viewing a project's Virtual Keys tab (`GET /projects/{id}/keys`, `POST /keys`, `POST /keys/{id}/revoke`), **Then** `admin` can manage all Virtual Keys across all projects, while `Project Developer` can view and manage all Virtual Keys within their **assigned projects** (binding keys to their own mTLS clients or project-accessible clients).

---

### User Story 3 - Streamlined Self-Service UX & Unified Key Onboarding (Priority: P3)

As a `Project Developer` or `admin`, I want an intuitive UI that displays human-readable owner info, clearly separates personal devices from system-wide clients (for Admins), and guides me from registering a device to the Project's Virtual Keys tab to generate Virtual Access Keys.

**Why this priority**: Improves developer onboarding speed and eliminates confusion between mTLS Client Certificates (hardware/machine identity) and Virtual Access Keys (project-scoped API tokens).

**Independent Test**: Register a new device in UI -> download `.crt`/`.key` -> see clear guidance/link to navigate to an assigned Project's Virtual Keys tab to generate a Virtual Key.

**Acceptance Scenarios**:

1. **Given** the Clients directory table, **When** rendered, **Then** each row displays the owner's avatar, full name, and email (resolved from SSO directory) rather than raw numeric `owner_id`.
2. **Given** an `admin` user on the Clients page, **When** viewing the table, **Then** quick filter tabs ("Tất cả hệ thống" vs "Thiết bị của tôi") and type/status filters allow rapid inspection.
3. **Given** a `Project Developer` after registering a device on "Thiết bị & Client", **When** downloading the certificate, **Then** the UI provides a clear next-step callout/link directing them to the **Virtual Keys** tab inside their Project detail page to generate API keys (keeping Virtual Key creation scoped inside Project detail pages).

---

### Edge Cases

- **Cross-User Virtual Key Binding**: A `Project Developer` who is a member of Project A attempts to call `POST /api/v1/gateway/keys` with a `client_id` owned by another user -> MUST fail with `HTTP 403 Forbidden`.
- **Owner Directory Lookup Miss**: If an `owner_id` no longer exists in the SSO directory (e.g. legacy string `"tech_lead"` or deleted user), the UI MUST gracefully fall back to displaying the raw identifier without crashing.
- **Revoked Client Cascade**: When a Developer or Admin revokes an mTLS client, all Virtual Access Keys bound to that client MUST be revoked atomically and reflected immediately in both the Clients and Project Keys views.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `GET /api/v1/gateway/clients` MUST enforce ownership scoping: `ADMIN` retrieves all clients (`list_all()`), while `PROJECT_DEVELOPER` retrieves only clients owned by `str(user_ctx.user_id)` (`list_by_owner_id()`).
- **FR-002**: `POST /api/v1/gateway/clients` MUST unconditionally set `owner_id = str(user_ctx.user_id)` from the verified SSO token for all callers (`ADMIN` and `PROJECT_DEVELOPER`), preventing `owner_id` spoofing or creating certificates on behalf of other users.
- **FR-003**: `POST /api/v1/gateway/clients/{client_id}/revoke` MUST verify `client.owner_id == str(user_ctx.user_id)` for `PROJECT_DEVELOPER`, returning `HTTP 403 Forbidden` on ownership mismatch. `ADMIN` MAY revoke any client in the system.
- **FR-004**: `GET /api/v1/gateway/projects/{id}/keys`, `POST /api/v1/gateway/keys`, and `POST /api/v1/gateway/keys/{key_id}/revoke` MUST enforce Project Membership for `PROJECT_DEVELOPER` (allowing Developers to view and manage all Virtual Keys within their assigned projects; `ADMIN` manages all projects).
- **FR-005**: `POST /api/v1/gateway/clients` MUST allow both `USER_DEVICE` and `APP_SERVER` for both `ADMIN` and `PROJECT_DEVELOPER`, with self-ownership enforced via `FR-002`.
- **FR-006**: The Frontend `ClientsTable` MUST resolve `owner_id` against the SSO User Directory (`useUserOptionsQuery`) to display owner name, email, and avatar, MUST support Admin filter views ("Tất cả hệ thống" vs "Thiết bị của tôi"), and `CertDownloadDialog` MUST provide a clear next-step link to `/projects` to create Virtual Keys inside the Project detail tab.

### Key Entities

- **RegisteredClient (`registered_clients`)**: Represents an mTLS hardware device (`USER_DEVICE`) or application server (`APP_SERVER`) owned by `owner_id` (SSO user ID string).
- **VirtualAccessKey (`virtual_access_keys`)**: Represents a project-scoped API key bound to a `(client_id, project_id)` pair.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0% cross-user data leakage — a `Project Developer` never sees, binds, or revokes another user's mTLS client or personal virtual key.
- **SC-002**: 100% of client rows in the UI display human-readable SSO owner profiles (name/email/avatar) when present in the directory.
- **SC-003**: Developers can complete the end-to-end flow (register device -> download mTLS cert -> generate Virtual Key) cleanly with clear status feedback.

## Assumptions

- `IExternalUserDirectoryService` (`/api/v1/users/options`) provides the authoritative mapping from integer `user_id` to `name`, `email`, and `avatar_url`.
- `RoleTier.OTHER` (`Trainer`, `Content`, etc.) remains completely blocked (`403 Forbidden`) from mTLS Client and Virtual Key management per Feature `019`.
