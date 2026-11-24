# Feature Specification: Pure SSO Authentication & Gateway Flow

**Feature Branch**: `018-pure-sso-gateway-auth`

**Created**: 2026-11-24

**Status**: Draft

**Input**: User description: "Lỗi Network Error, bạn hãy xem xét nếu đang fix theo hướng chấp vá cả FE và BE, hãy đập đi xây lại /speckit-specify"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Seamless SSO Login & Immediate Dashboard Redirection (Priority: P1)

As an authenticated organization user with a central DUT-AI account, I want to log into the Gateway & Vault platform using my single enterprise identity so that I gain access to administrative dashboards without encountering network preflight errors, infinite loops, or false failure alerts.

**Why this priority**: Core access gate for the entire platform. Without reliable authentication through the Zero-Trust entrypoint, no administrative or operational workflows can be performed by authorized users.

**Independent Test**: Can be tested end-to-end by providing valid DUT-AI credentials on the login page; the system verifies credentials against the central IdP, establishes an authenticated session, and immediately lands on the dashboard with user profile hydrated.

**Acceptance Scenarios**:

1. **Given** a user navigating to `/login`, **When** they submit valid DUT-AI credentials, **Then** the system receives an authenticated SSO token from the central IdP, stores session state, and redirects to the dashboard within 2 seconds.
2. **Given** an active session, **When** the user accesses protected pages (such as `/projects`, `/clients`, or `/vault`), **Then** the platform presents the requested dashboard components without prompting for re-authentication.

---

### User Story 2 - Gateway-Level CORS Preflight & Transparent Routing (Priority: P1)

As a frontend web client executing browser network requests against the API Gateway, I want all cross-origin requests (including preflight `OPTIONS` calls) to be resolved with standard CORS headers so that client-side network calls never fail with browser `Network Error` or `405 Method Not Allowed`.

**Why this priority**: Cross-origin preflight failure completely blocks the browser from transmitting HTTP payloads to the backend API, causing false-negative authentication failures even when backend logic is healthy.

**Independent Test**: Can be tested by sending `OPTIONS` preflight requests from the web origin (`http://localhost:3000`) to the Gateway proxy entrypoint (`http://localhost:9080/api/v1/*`); the Gateway returns `200 OK` with valid `Access-Control-Allow-*` headers.

**Acceptance Scenarios**:

1. **Given** a web browser initiating a cross-origin preflight request for `/api/v1/auth/sso-login`, **When** the request arrives at the Gateway entrypoint, **Then** the Gateway responds with `HTTP 200 OK` and allowed methods (`POST, GET, OPTIONS`), allowed headers, and allowed credentials.
2. **Given** a valid authenticated request carrying credentials, **When** forwarded through the Gateway, **Then** downstream backend handlers receive all required headers and cookies intact.

---

### User Story 3 - Resilient Profile Hydration & Session Guarding (Priority: P2)

As an authenticated administrator, I want my profile (including name, roles, permissions, and avatar) to be retrieved seamlessly from the central directory, and cached resiliently, so that navigation between platform features is snappy and shielded from temporary directory service hiccups.

**Why this priority**: Authorizes role-based interface elements and client management features without repeated heavy round-trips to the remote identity provider.

**Independent Test**: Can be tested by loading the dashboard after initial login; the profile renders with correct role badges and permissions, and subsequent page loads leverage the caching layer.

**Acceptance Scenarios**:

1. **Given** an authenticated user landing on `/dashboard`, **When** profile hydration executes, **Then** the user's name, email, and permissions display accurately.
2. **Given** temporary network latency or intermittent failure of the central user directory, **When** profile queries run, **Then** the system utilizes cached responses or displays a non-destructive retry state rather than logging the user out.

---

### User Story 4 - Clear and Accurate Error Communication (Priority: P3)

As an end user attempting to log in, I want clear, accurate error messages when authentication fails so that I understand whether my password was incorrect, my account was locked, or a network connectivity issue occurred.

**Why this priority**: Prevents user frustration and reduces administrative support overhead by distinguishing credential errors from infrastructure timeouts.

**Independent Test**: Can be tested by submitting deliberate invalid credentials; the system returns an informative error message explaining that the credentials were not recognized by the central IdP.

**Acceptance Scenarios**:

1. **Given** an invalid password submission, **When** the authentication request fails, **Then** the interface displays an informative credential error message rather than a generic network failure banner.
2. **Given** a network disconnection from the central IdP, **When** authentication is attempted, **Then** the system displays a clear connectivity notice advising the user to try again shortly.

---

### Edge Cases

- **CORS Preflight on Custom Headers**: When the browser sends custom authentication headers, the gateway preflight handler must allow the exact requested headers without dropping authorization tokens.
- **Clock Drift & Token Expiration**: When an SSO token reaches its expiration boundary during an active user session, the system must prompt the user with a graceful re-login prompt rather than a broken page state.
- **Deactivated/Revoked SSO User**: When an SSO account is revoked in the central directory, the cascade revocation mechanism must immediately terminate active virtual keys and invalidate cached user profiles.
- **Cookie Domain Mismatches**: When running across different local ports (e.g., port 3000 and port 9080), session tokens must be stored in accessible client storage and transmitted via standard Authorization headers to avoid cookie scope rejections.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST delegate all user authentication exclusively to the central DUT-AI Identity Provider, with zero local database password storage.
- **FR-002**: System MUST configure the API Gateway entrypoint to handle all preflight `OPTIONS` requests uniformly, returning appropriate CORS headers for authorized origins.
- **FR-003**: System MUST provide an SSO login interface accepting user credentials, transmitting them to the backend control plane, and receiving structured session tokens.
- **FR-004**: System MUST maintain authenticated session tokens in secure client-side storage and transmit them via Bearer headers on subsequent API requests.
- **FR-005**: System MUST redirect authenticated users directly to the protected dashboard upon successful credential verification.
- **FR-006**: System MUST hydrate the authenticated user's profile and permissions from the central user directory service, caching results in the service layer.
- **FR-007**: System MUST invalidate cached user sessions and cascade-revoke active client credentials upon receiving user deactivation events.
- **FR-008**: System MUST distinguish between invalid credentials, network unreachable errors, and authorization rejections, presenting distinct, helpful user feedback.

### Key Entities *(include if feature involves data)*

- **SsoSession**: Represents an active authenticated user session containing access token, expiration metadata, and user identity reference.
- **UserProfile**: Represents the user's identity attributes (native integer ID, email, display name, avatar, role names, and assigned permissions) obtained from the central directory.
- **GatewayRoute**: Defines the routing rule mapping public API endpoints through the Zero-Trust gateway to backend services, including CORS and header transformation policies.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete SSO authentication and view their populated dashboard in under 2 seconds under standard network conditions.
- **SC-002**: 100% of browser preflight `OPTIONS` requests to the gateway API resolve with HTTP 200 and valid CORS response headers, eliminating browser `Network Error` blocks.
- **SC-003**: 0% of user passwords or credential hashes are stored in the local platform database, maintaining strict compliance with the project constitution.
- **SC-004**: In the event of central IdP communication errors, 100% of failures present human-readable error descriptions rather than unhandled exception states.

## Assumptions

- The central DUT-AI Identity Provider (`https://manage.dutai.io.vn`) is accessible and serves standard SSO authentication and user directory endpoints.
- The web frontend runs on modern standards-compliant web browsers supporting ES2022, Fetch API, and standard Web Storage.
- Development and local staging environments route web requests through the Apache APISIX gateway proxy to mirror production Zero-Trust network topologies.
