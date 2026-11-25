# Feature Specification: Regular Dev Device Self-Registration & Project Developer Key Binding

**Feature Branch**: `021-dev-device-project-binding`

**Created**: 2026-11-25

**Status**: Draft

**Input**: User description: "Hiện tại có 3 loại người dùng sử dụng hệ thống này, 1 là admin, có toàn quyền quản lý tất cả, 2 là project developer quản lý từng dự án được assigne, 3 là dev bình thường, họ có thể tự đăng ký thiết bị của mình, sau đó project developer sẽ add key của dev vào từng dự án á"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Regular Developer Self-Registers Personal mTLS Device (Priority: P1) 🎯 MVP

As a regular developer (`Tier 3 / Other Roles`, e.g., `Trainer`, `Content`, `member`), I need to access the "Thiết bị & Client" page to register my own mTLS device, download my certificate (`client.crt` / `client.key`), and view or revoke my own devices, so that a Project Developer can later bind my device to a project.

**Why this priority**: Currently `Tier 3` users are blocked (`403 Forbidden`) from `/clients` and the sidebar hides the "Thiết bị & Client" link. Without self-registration, regular developers cannot obtain hardware mTLS certificates for their workstations.

**Independent Test**: Log in as a `Tier 3` user (`user_id=20`). Verify "Thiết bị & Client" is visible in the sidebar. Register a new device (`owner_id` automatically locked to `"20"`), download `client.crt`/`client.key`, and verify the user sees **only** their own devices (cannot see or revoke Admin's or other developers' devices).

**Acceptance Scenarios**:

1. **Given** a `Tier 3` user, **When** viewing the navigation sidebar, **Then** "Thiết bị & Client" (`/clients`) is accessible.
2. **Given** a `Tier 3` user on `/clients`, **When** registering a new mTLS device (`POST /api/v1/gateway/clients`), **Then** `owner_id` is locked to `str(user_ctx.user_id)`, **only `USER_DEVICE` is permitted** (attempting `APP_SERVER` returns `HTTP 403 Forbidden`), and the certificate is issued (`201 Created`).
3. **Given** a `Tier 3` user, **When** listing clients (`GET /api/v1/gateway/clients`), **Then** ONLY clients owned by `str(user_ctx.user_id)` are returned; attempting to revoke another user's client returns `HTTP 403 Forbidden`.

---

### User Story 2 - Project Developer Binds Developer Devices to Assigned Projects (Priority: P2)

As a `Project Developer` managing an assigned project, I need to select a registered developer's mTLS device inside the project's **Virtual Keys** tab and generate a Virtual Access Key binding that device to my assigned project, so that the developer can call Gateway APIs for that project.

**Why this priority**: Currently `GET /clients` returns only the Project Developer's own devices, so a Project Developer cannot see or select another developer's registered device in the `GenerateKeyModal` to add them to a project!

**Independent Test**: Regular Dev (`user_id=20`, member of Project A) registers "Dev 20 Laptop". Project Developer (`user_id=10`, member of Project A) opens Project A -> Virtual Keys -> Generate Key -> sees "Dev 20 Laptop" (belonging to Project A member `user_id=20`) -> generates Virtual Key (`vk_live_...`). Devices of non-members are NOT listed.

**Acceptance Scenarios**:

1. **Given** a `Project Developer` assigned to Project A, **When** opening the "Tạo Virtual Key" modal inside Project A, **Then** the device selector lists active mTLS devices belonging to **members assigned to Project A** (`project_members`), displaying each device's owner name/email/avatar.
2. **Given** a `Project Developer` on `/clients`, **When** managing their own devices (`POST /clients/{id}/revoke`), **Then** they can revoke their own devices, while revoking another user's device remains `403 Forbidden` (unless `admin`).
3. **Given** a `Project Developer` inside Project A's Virtual Keys tab, **When** generating or revoking a Virtual Key (`POST /keys`, `POST /keys/{id}/revoke`), **Then** the operation succeeds (`201`/`200`) for Project A and fails (`403`) for unassigned Project B.

---

### User Story 3 - Admin Full Governance & Regular Dev Read-Only Key Visibility (Priority: P3)

As an `admin`, I retain full governance over all projects, all registered devices, and all Virtual Keys across the system; and as a regular developer (`Tier 3`), I can view (read-only) the Virtual Keys issued for my own devices inside projects I belong to.

**Why this priority**: Ensures clear visibility and zero confusion during team onboarding while keeping mutation authority strictly with Admins and Project Developers.

**Independent Test**: Verify `admin` sees all clients and all project keys. Verify `Tier 3` user (`user_id=20`) opens Project A -> Virtual Keys tab -> sees only Virtual Keys bound to their own devices (read-only; "Tạo Virtual Key" and "Thu hồi" buttons hidden and rejected with `403` on API).

**Acceptance Scenarios**:

1. **Given** an `admin`, **When** accessing `/clients` or any project's Virtual Keys tab, **Then** all system devices and keys are visible and manageable.
2. **Given** a `Tier 3` user assigned to Project A, **When** opening Project A detail tabs, **Then** the **Virtual Keys** tab is visible in **read-only mode**, showing **only Virtual Keys bound to devices owned by that `Tier 3` user** (all create/revoke actions are hidden on UI and return `403 Forbidden` on API).

---

### Edge Cases

- **Unassigned Project Key Binding**: A `Project Developer` attempts to generate a Virtual Key for a project they are NOT a member of -> `HTTP 403 Forbidden`.
- **Revoked Device**: If a `Tier 3` developer revokes their own mTLS device, all Virtual Keys bound to that device across all projects are immediately revoked.
- **Unassigned Developer Device**: If a `Tier 3` developer has registered a device, they cannot use it against a project until a `Project Developer` (of that project) or `admin` generates a Virtual Key binding it to that project.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `Tier 3` (`OTHER`) users MUST be granted access to `/clients` (`GET /gateway/clients` scoped to their own `owner_id`, `POST /gateway/clients` self-issued and restricted to `USER_DEVICE` only — `APP_SERVER` returns `403 Forbidden`, `POST /gateway/clients/{id}/revoke` scoped to their own `owner_id`) and see "Thiết bị & Client" in the sidebar navigation.
- **FR-002**: When `PROJECT_DEVELOPER` opens the Virtual Key generation flow for an assigned project, the backend MUST provide `GET /api/v1/gateway/projects/{project_id}/available-clients` returning active mTLS devices owned by **members assigned to that project (`project_members`)** (`ADMIN` sees all active devices).
- **FR-003**: `GET /api/v1/gateway/projects/{project_id}/keys` MUST allow assigned `Tier 3` (`OTHER`) users to view (read-only) Virtual Keys bound to their **own** mTLS devices (`client.owner_id == str(user_ctx.user_id)`), while `ADMIN` and assigned `PROJECT_DEVELOPER` see and manage all Virtual Keys of the project. `POST /keys` and `POST /keys/{id}/revoke` MUST remain `403 Forbidden` for `Tier 3`.
- **FR-004**: `PROJECT_DEVELOPER` MUST remain blocked (`HTTP 403 Forbidden`) from revoking another user's mTLS client on `/clients/{id}/revoke`, while retaining full authority to generate and revoke Virtual Keys inside their assigned projects.
- **FR-005**: `ADMIN` retains unrestricted visibility and management over all mTLS clients, all projects, and all Virtual Keys.
- **FR-006**: The `GenerateKeyModal` UI MUST display owner name/email/avatar alongside each device name so Project Developers can accurately identify which project member's device they are binding to the project. The Project **Virtual Keys** tab MUST render in read-only mode for `Tier 3` users.

### Key Entities

- **RegisteredClient (`registered_clients`)**: Self-issued mTLS device owned by `owner_id` (any authenticated user: `ADMIN`, `PROJECT_DEVELOPER`, or `OTHER`).
- **VirtualAccessKey (`virtual_access_keys`)**: Project-scoped access key created by `ADMIN` or `PROJECT_DEVELOPER` binding a developer's `client_id` to a `project_id`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `Tier 3` developers can self-register their mTLS device and download certificates without admin intervention.
- **SC-002**: A `Project Developer` can discover a regular developer's registered device and bind a Virtual Key for their assigned project in under 3 clicks.
- **SC-003**: Zero cross-user device revocation is possible by non-admin users (`100%` return `403 Forbidden`).

## Assumptions

- Project Developers are responsible for onboarding developers into their assigned projects by issuing Virtual Keys for those developers' registered devices.
- Machine-level key permissions (`key_permissions`) and project membership (`project_members`) continue to govern Vault and Project access.
