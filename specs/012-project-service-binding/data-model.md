# Data Model: Project Upstream Service Binding & Quota Governance

**Feature Branch**: `012-project-service-binding`
**Created**: 2026-11-23

## Entity Relationship Overview

```mermaid
erDiagram
    PROJECT ||--o{ PROJECT_UPSTREAM_ALLOWLIST : binds
    UPSTREAM_SERVICE ||--o{ PROJECT_UPSTREAM_ALLOWLIST : is_bound
    PROJECT ||--o{ QUOTA_POLICY : governs
    UPSTREAM_SERVICE ||--o{ QUOTA_POLICY : applies_to

    PROJECT {
        string id PK "ULID (26 chars)"
        string name "Project name"
        string slug UK "Unique slug"
        string description "Optional description"
        datetime created_at "Creation timestamp"
        datetime updated_at "Update timestamp"
    }

    UPSTREAM_SERVICE {
        string id PK "ULID (26 chars)"
        string name "Service name"
        string slug UK "Unique slug"
        string base_url "Target URL"
        string auth_type "BEARER_TOKEN | API_KEY | BASIC | NONE"
        string encrypted_credential "AES-256-GCM ciphertext"
        int timeout_seconds "Default 30s"
        bool is_active "Default true"
    }

    PROJECT_UPSTREAM_ALLOWLIST {
        string project_id PK, FK "References projects.id ON DELETE CASCADE"
        string service_id PK, FK "References upstream_services.id ON DELETE CASCADE"
    }

    QUOTA_POLICY {
        string id PK "ULID (26 chars)"
        string project_id FK "References projects.id ON DELETE CASCADE"
        string service_id FK "References upstream_services.id ON DELETE CASCADE"
        string client_id FK "Nullable, references registered_clients.id"
        int rate_limit_rpm "Requests per minute, default 60"
        int quota_daily "Requests per day, default 10,000"
        bool is_active "Default true"
        datetime created_at "Creation timestamp"
        datetime updated_at "Update timestamp"
    }
```

## Domain Data Transfer Objects (DTOs)

### 1. `ProjectAllowedServiceDTO` (Response DTO)
Represents a bound upstream service including its active quota policy.
- `service_id`: `str`
- `service_name`: `str`
- `service_slug`: `str`
- `base_url`: `str`
- `auth_type`: `str`
- `is_service_active`: `bool`
- `rate_limit_rpm`: `int` (requests per minute)
- `quota_daily`: `int` (requests per day)
- `is_quota_active`: `bool`
- `bound_at`: `datetime`

### 2. `BindServiceToProjectRequest` (Request DTO)
Payload sent by frontend to authorize an upstream service for a project.
- `service_id`: `str` (ULID of upstream service, min_length=26, max_length=26)
- `rate_limit_rpm`: `int` (>= 1, default 60)
- `quota_daily`: `int` (>= 1, default 10,000)

### 3. `UpdateServiceQuotaRequest` (Request DTO)
Payload sent to adjust quota limits for an already bound service.
- `rate_limit_rpm`: `int` (>= 1)
- `quota_daily`: `int` (>= 1)

## Invariants & Validation Rules

1. **Uniqueness**: A service can only be bound to a project once. Primary key `(project_id, service_id)` on `project_upstream_allowlist` guarantees relational uniqueness.
2. **Quota Bounds**:
   - `rate_limit_rpm` must be an integer between 1 and 100,000.
   - `quota_daily` must be an integer between 1 and 10,000,000.
3. **Cascading Cleanliness**:
   - Deleting a project automatically deletes its allowlist entries and quota policies.
   - Deleting an upstream service automatically cleans up all associated project allowlists and quota policies.
4. **Zero-Trust Default**: If a project has no record in `project_upstream_allowlist` for a given `service_id`, any API gateway call to that service is denied with `HTTP 403 Forbidden`.
