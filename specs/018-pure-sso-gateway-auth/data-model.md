# Data Model: Pure SSO Authentication & Gateway Flow

## Entities & Schemas

### 1. UserLoginRequest (Input DTO)
Represents the credentials submitted by an end user on the login form.

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | `EmailStr` | Yes | Valid email address of DUT-AI organization account |
| `password` | `str` | Yes | Account password for central SSO IdP verification |

### 2. TokenResponse (Output DTO)
Returned by the backend upon successful credential validation against the central DUT-AI IdP.

| Field | Type | Required | Description |
|---|---|---|---|
| `access_token` | `str` | Yes | Cryptographically signed JWT issued by central IdP |
| `token_type` | `str` | Yes | Token type identifier, defaults to `"bearer"` |
| `expires_in` | `int` | Yes | Lifetime of access token in seconds (e.g. 1800) |

### 3. UserProfile / UserResponse (Domain Profile)
Represents the authenticated user profile retrieved from the central directory.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `int` | Yes | Strict integer identifier from DUT-AI Manage IdP |
| `email` | `str` | Yes | Unique organization email |
| `name` | `str | None` | No | Display name of the user |
| `role` | `str` | Yes | Primary user role (e.g. `"admin"`, `"member"`) |
| `avatar_url` | `str | None` | No | Absolute URL to user avatar in storage |
| `status` | `str` | Yes | Account status, e.g. `"ACTIVE"` |
| `role_names` | `list[str]` | Yes | All roles assigned to user in IdP |
| `permissions` | `list[str]` | Yes | Granular action permissions (e.g. `["user:read", "*"]`) |

### 4. GatewayControlPlaneRoute (Gateway Configuration)
Defines the APISIX route configuration for the control plane API.

| Field | Type | Description |
|---|---|---|
| `uri` | `str` | `/api/*` |
| `upstream` | `object` | Nodes pointing to FastAPI Control Plane backend |
| `plugins.cors` | `object` | APISIX CORS plugin configuration with credentials and methods |

## State Transitions

```text
[Unauthenticated]
       │
       ▼ (Submit Email & Password to /api/v1/auth/sso-login)
[SSO Verification via Central IdP]
       │
       ├─► Invalid (401) ──► Display "Email hoặc mật khẩu SSO không chính xác"
       │
       ▼ Valid (200 OK + JWT)
[Persist Tokens] (localStorage + cookie)
       │
       ▼ (window.location.assign("/dashboard"))
[Dashboard Mount & Profile Hydration] (GET /api/v1/auth/me)
       │
       ├─► Cache Miss ──► Query IdP & Cache in Redis (TTL 300s)
       │
       ▼
[Fully Authenticated & Hydrated Session]
```
