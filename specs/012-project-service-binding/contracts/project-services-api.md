# API Contracts: Project Upstream Service Binding & Quota Governance

**Feature Branch**: `012-project-service-binding`
**Base URL**: `/api/v1/gateway`
**Auth**: Bearer Token or Authenticated Session

---

### 1. List Project Allowed Services

Retrieve all upstream services authorized for a specific project along with their active quota policies.

- **Method**: `GET`
- **Path**: `/api/v1/gateway/projects/{project_id}/services`
- **Path Parameters**:
  - `project_id` (string, required): 26-character ULID of the project.

#### Response: `200 OK`
```json
[
  {
    "service_id": "01JM4X9Y8Z123456789ABCDEFG",
    "service_name": "OpenAI API",
    "service_slug": "openai-api",
    "base_url": "https://api.openai.com/v1",
    "auth_type": "BEARER_TOKEN",
    "is_service_active": true,
    "rate_limit_rpm": 120,
    "quota_daily": 50000,
    "is_quota_active": true,
    "bound_at": "2026-11-23T08:00:00Z"
  }
]
```

#### Response: `404 Not Found`
```json
{
  "detail": "Project '01JM4...' not found"
}
```

---

### 2. Bind Upstream Service to Project

Authorize an existing upstream service for the project and configure its traffic governance quotas.

- **Method**: `POST`
- **Path**: `/api/v1/gateway/projects/{project_id}/services`
- **Path Parameters**:
  - `project_id` (string, required): ULID of the project.
- **Request Body**:
```json
{
  "service_id": "01JM4X9Y8Z123456789ABCDEFG",
  "rate_limit_rpm": 60,
  "quota_daily": 10000
}
```

#### Response: `201 Created`
```json
{
  "service_id": "01JM4X9Y8Z123456789ABCDEFG",
  "service_name": "OpenAI API",
  "service_slug": "openai-api",
  "base_url": "https://api.openai.com/v1",
  "auth_type": "BEARER_TOKEN",
  "is_service_active": true,
  "rate_limit_rpm": 60,
  "quota_daily": 10000,
  "is_quota_active": true,
  "bound_at": "2026-11-23T14:55:00Z"
}
```

#### Error Responses:
- `400 Bad Request / 409 Conflict`: Service is already bound to this project.
```json
{
  "detail": "Service '01JM4...' is already bound to project '01JM2...'"
}
```
- `404 Not Found`: Project or Upstream Service does not exist.
```json
{
  "detail": "Upstream service '01JM4...' not found"
}
```
- `422 Unprocessable Entity`: Validation failure on input parameters.

---

### 3. Update Service Quota Policy

Modify the rate limit RPM or daily request quota for an already-bound upstream service.

- **Method**: `PUT`
- **Path**: `/api/v1/gateway/projects/{project_id}/services/{service_id}/quota`
- **Path Parameters**:
  - `project_id` (string, required): Project ULID.
  - `service_id` (string, required): Upstream Service ULID.
- **Request Body**:
```json
{
  "rate_limit_rpm": 120,
  "quota_daily": 25000
}
```

#### Response: `200 OK`
```json
{
  "service_id": "01JM4X9Y8Z123456789ABCDEFG",
  "service_name": "OpenAI API",
  "service_slug": "openai-api",
  "base_url": "https://api.openai.com/v1",
  "auth_type": "BEARER_TOKEN",
  "is_service_active": true,
  "rate_limit_rpm": 120,
  "quota_daily": 25000,
  "is_quota_active": true,
  "bound_at": "2026-11-23T14:55:00Z"
}
```

#### Error Responses:
- `404 Not Found`: Project, Service, or Binding not found.

---

### 4. Revoke / Unbind Upstream Service from Project

Revoke a project's access to an upstream service. This removes the association and deletes the associated quota policy.

- **Method**: `DELETE`
- **Path**: `/api/v1/gateway/projects/{project_id}/services/{service_id}`
- **Path Parameters**:
  - `project_id` (string, required): Project ULID.
  - `service_id` (string, required): Upstream Service ULID.

#### Response: `204 No Content`
*(Empty response body)*

#### Error Responses:
- `404 Not Found`: Service is not bound to this project.
```json
{
  "detail": "Service '01JM4...' is not bound to project '01JM2...'"
}
```
