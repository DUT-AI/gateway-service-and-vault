# API Contracts: Standardized 3-Tier RBAC & Project Membership

**Feature**: `019-standardized-rbac-vault` | **Date**: 2026-11-25

## 1. Project Membership Management (`ADMIN` Only)

### 1.1 List Project Members
- **URL**: `GET /api/v1/gateway/projects/{project_id}/members`
- **Auth**: Bearer JWT (`ADMIN` required; `403 Forbidden` for `PROJECT_DEVELOPER` / `OTHER`)
- **Response 200 OK**:
```json
[
  {
    "id": "01M8...",
    "project_id": "01M8...",
    "user_id": 12,
    "added_by": 1,
    "created_at": "2026-11-25T13:00:00Z"
  }
]
```

### 1.2 Assign Member to Project
- **URL**: `POST /api/v1/gateway/projects/{project_id}/members`
- **Auth**: Bearer JWT (`ADMIN` required; `403 Forbidden` otherwise)
- **Request Body**:
```json
{
  "user_id": 12
}
```
- **Response 201 Created**: `ProjectMemberResponse`

### 1.3 Remove Member from Project
- **URL**: `DELETE /api/v1/gateway/projects/{project_id}/members/{user_id}`
- **Auth**: Bearer JWT (`ADMIN` required; `403 Forbidden` otherwise)
- **Response 204 No Content**

---

## 2. Authorization Matrix Across Existing Endpoints

| Endpoint | `ADMIN` | `PROJECT_DEVELOPER` | `OTHER` (`Trainer`, `Content`, etc.) |
|---|---|---|---|
| `GET /gateway/projects` | All projects | Assigned projects only | Assigned projects only |
| `POST /gateway/projects` | Allowed (`201`) | `403 Forbidden` | `403 Forbidden` |
| `GET /gateway/projects/{id}` | Allowed (`200`) | Assigned only (`403` if unassigned) | Assigned only (`403` if unassigned) |
| `POST /gateway/services` (global) | Allowed (`201`) | `403 Forbidden` | `403 Forbidden` |
| `GET /gateway/services` | Allowed (`200`) | Allowed (`200`) | `403 Forbidden` |
| `PUT /gateway/projects/{id}/services/{svc_id}/quota` | Allowed (`200`) | `403 Forbidden` | `403 Forbidden` |
| `GET /gateway/projects/{id}/services` | Allowed (`200`) | Assigned only | Assigned only |
| `POST/DELETE /gateway/projects/{id}/keys` | Allowed | Assigned only | `403 Forbidden` |
| `POST/DELETE /gateway/projects/{id}/clients` | Allowed | Assigned only | `403 Forbidden` |
| `GET /vault/projects/{id}/secrets` | All secrets | All secrets (if assigned) | Only created or granted keys (if assigned) |
| `POST /vault/projects/{id}/secrets` | Allowed | Allowed (if assigned) | Allowed (if assigned, auto-granted to creator) |
| `POST/DELETE /vault/projects/{id}/permissions` | Allowed | `403 Forbidden` | `403 Forbidden` |
| `GET /vault/projects/{id}/stream` | All events | All project events (if assigned) | Only permitted key events (if assigned) |
