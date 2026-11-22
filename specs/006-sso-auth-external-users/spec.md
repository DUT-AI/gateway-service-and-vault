# Feature Specification: SSO-Only Authentication & External User Directory

**Feature Branch**: `006-sso-auth-external-users`

**Created**: 2026-11-23

**Status**: Draft

**Input**: User description: "Hãy chỉnh sửa lại phần Auth, chỉ auth qua SSO, ko quản lý tài khoản riêng ở db này, về người dùng thì sẽ get user qua 1 service khác gồm api get toàn bộ user: https://manage.dutai.io.vn/api/v1/users/options và get chi tiết 1 user https://manage.dutai.io.vn/api/v1/users/{id} bạn có thể test thông qua access_token này [token provided]. Nhớ id là int, không là string nhé, không chơi ép kiểu để chấp vá"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Pure SSO Authentication Without Local User Accounts (Priority: P1) 🎯 MVP

As an enterprise user or developer accessing the Gateway & Vault platform, I want to authenticate solely through our central SSO Identity Provider (DUT-AI Manage), without the platform storing or managing passwords, user credentials, or local registration records in its own database.

**Why this priority**: Eliminates redundant credential stores, prevents credential desynchronization across platforms, and ensures single-point identity lifecycle governance without maintaining a separate user database.

**Independent Test**: An authenticated user accesses protected platform endpoints providing only an SSO access token (via Cookie or Bearer header). The system validates the token against the central SSO authority and grants access. Attempting to register a local username/password is rejected or disabled because local credential management does not exist.

**Acceptance Scenarios**:

1. **Given** a user with a valid SSO token issued by `manage.dutai.io.vn`, **When** the user sends a request to `/api/v1/auth/me` with the token in `Authorization: Bearer <token>` or `Cookie: access_token=<token>`, **Then** the platform returns the user's profile with their native integer identifier (`id: int`), roles, and permissions.
2. **Given** a client attempting to access protected resources with an invalid, expired, or tampered token, **When** the request is received, **Then** the system immediately rejects it with HTTP 401 Unauthorized without consulting any local database tables.
3. **Given** a user attempting to invoke local account registration (`/register`) or local password-based login, **When** the request arrives, **Then** the system directs the user to the SSO flow and disallows creating independent user credentials in the local database.
4. **Given** a user requesting SSO login with valid SSO credentials via `/api/v1/auth/sso-login`, **When** the external SSO service authenticates the user, **Then** the platform sets secure `access_token` and `refresh_token` cookies and returns token metadata without persisting credentials locally.

---

### User Story 2 - Remote User Directory Listing for Platform Collaboration (Priority: P2)

As a project administrator or developer configuring projects, mTLS certificates, or key-level secret permissions, I need to browse available users from the central directory (`/users/options`) so that I can select and assign permissions or project ownership to team members without the local platform maintaining a copy of the user table.

**Why this priority**: Core platform features (such as key permissions, audit logs, and project ownership) require referencing genuine organization members from the central directory.

**Independent Test**: Call the user options endpoint with a valid SSO token. The platform retrieves and returns the current list of users from `https://manage.dutai.io.vn/api/v1/users/options`, where each entry exposes an integer `id`, full name, email, and avatar URL.

**Acceptance Scenarios**:

1. **Given** an authenticated user or admin calling the user options endpoint (`GET /api/v1/users/options`), **When** the external directory responds successfully, **Then** the platform returns a list of user summary objects where every user identifier is strictly an integer (`id: int`).
2. **Given** an unauthenticated request to the user options endpoint, **When** the request is received, **Then** the platform returns HTTP 401 Unauthorized.
3. **Given** a network disruption or temporary outage on the external user service, **When** a user calls the options endpoint, **Then** the system gracefully returns HTTP 502/504 with an informative message rather than crashing.

---

### User Story 3 - Detailed User Profile Inspection by Integer ID (Priority: P3)

As an administrator or platform auditor, I need to inspect the full profile details, roles, and status of a specific user by their integer identifier (`/users/{id}`) so that I can audit permissions and review user status directly against the central source of truth.

**Why this priority**: Enables deep identity verification, audit trail mapping, and permission checks against the live state of any team member in the organization.

**Independent Test**: Query `/api/v1/users/{id}` with a valid integer ID (e.g. `id=1`). The system returns the full profile (roles, status, phone number, permissions) directly from `https://manage.dutai.io.vn/api/v1/users/{id}`. If an invalid or non-integer ID is provided, the request is immediately rejected.

**Acceptance Scenarios**:

1. **Given** an authenticated caller and an existing user with integer ID `1`, **When** the caller requests `GET /api/v1/users/1`, **Then** the platform returns the full user profile with `id: 1` as an integer, including name, email, roles, and permissions.
2. **Given** a caller requesting a user ID that does not exist on the external directory, **When** the external service returns a 404 response, **Then** the platform returns HTTP 404 Not Found.
3. **Given** a caller attempting to pass a non-integer value (e.g. `/api/v1/users/abc`), **When** the request is received, **Then** the platform rejects the request with HTTP 422 Unprocessable Entity (strictly enforcing integer routing).

---

### Edge Cases

- **Non-integer User IDs**: The system must enforce integer constraints at the routing and validation level. Any non-integer identifier MUST be rejected with HTTP 422 validation error.
- **SSO Token Revocation / Expiry**: If a token expires while a user is actively interacting with the platform, all requests MUST promptly return HTTP 401 and not rely on stale local caches.
- **External Directory Rate Limiting / Timeout**: Upstream HTTP calls to `manage.dutai.io.vn` must configure explicit connection and read timeouts (e.g. 10s) and handle non-200 responses with standardized HTTP exception codes.
- **Data Type Integrity**: User identifiers must remain integer typed throughout all internal layers (domain entities, DTOs, service boundaries). Type coercion hacks (such as converting string to int and back) are forbidden.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Domain 1: SSO Authentication & Local Credential Removal
- **FR-001**: The platform MUST NOT store user passwords, password hashes, or local account credentials in the local database.
- **FR-002**: All authentication MUST be validated exclusively through the central DUT-AI SSO Identity Provider (`https://manage.dutai.io.vn`).
- **FR-003**: The platform MUST accept SSO authentication via `Authorization: Bearer <token>` header or `access_token` cookie.
- **FR-004**: The `/api/v1/auth/me` endpoint MUST retrieve current user details directly from the validated SSO identity context.
- **FR-005**: Local account creation endpoints (`/api/v1/auth/register`) and local password login MUST be eliminated or disabled in favor of `/api/v1/auth/sso-login`.

#### Domain 2: External User Directory Integration
- **FR-006**: The platform MUST provide an endpoint (`GET /api/v1/users/options`) that delegates to `https://manage.dutai.io.vn/api/v1/users/options` to list user choices.
- **FR-007**: The platform MUST provide an endpoint (`GET /api/v1/users/{id}`) that delegates to `https://manage.dutai.io.vn/api/v1/users/{id}` to fetch specific user details.
- **FR-008**: User identifiers in user options and user detail endpoints MUST be strictly represented and validated as integers (`id: int`).
- **FR-009**: All upstream communication with the external user directory MUST propagate the caller's SSO authorization credential to maintain upstream access control.

#### Domain 3: Type Discipline & Architectural Integrity
- **FR-010**: All user identity models, DTOs, and domain references across the codebase MUST use integer (`int`) for user identifiers.
- **FR-011**: Zero type-coercion workarounds (e.g. casting strings to integers or storing integer IDs as arbitrary strings) are permitted in user identification logic.

---

### Key Entities

- **ExternalUserOption**: Summary representation of a user from the directory. Contains `id: int`, `name: str`, `email: str`, and `avatar_url: str | None`.
- **ExternalUserDetail**: Full profile representation of a user from the directory. Contains `id: int`, `name: str`, `email: str`, `phone_number: str | None`, `status: str`, `role_ids: list[int]`, `role_names: list[str]`, `permissions: list[str]`, `avatar_url: str | None`, and related profile metadata.
- **SsoSession**: Validated user identity session extracted from an authentic SSO JWT or remote IdP validation check. Contains integer user ID, name, email, roles, and permissions.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

1. **Zero Local User Credentials**: The local database contains 0 user passwords, password hashes, or local registration records.
2. **100% SSO-Governed Access**: 100% of user authentication requests are verified against the central SSO Identity Provider.
3. **Strict Integer Typing**: 100% of user directory queries and profile payloads serialize user IDs as native integers (`id: int`).
4. **Real-time Directory Freshness**: Updates made to user roles or profile information on the central directory are reflected immediately in the platform on subsequent requests without stale local caching.
5. **Sub-second Directory Access**: Directory options and single-user lookups complete within 1 second under normal network conditions.
