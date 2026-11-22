# Research: SSO-Only Authentication & Remote User Directory Integration

**Feature Branch**: `006-sso-auth-external-users`  
**Date**: 2026-11-23  

---

## 1. Remote API Investigation & Endpoints Analysis

### Target Service
- **Base URL**: `https://manage.dutai.io.vn` (configurable via `SSO_DUTAI_BASE_URL` in `.env`)
- **Authentication**: `Authorization: Bearer <token>` or Cookie `access_token=<token>`

### Endpoint 1: User Options Directory
- **Method & Path**: `GET https://manage.dutai.io.vn/api/v1/users/options`
- **Response Format**:
  ```json
  {
    "is_success": true,
    "status_code": 200,
    "data": [
      {
        "id": 3,
        "name": "Phạm Thị Thảo Nguyên",
        "email": "thaonguyenhead@gmail.com",
        "avatar_url": "https://minio.dutai.site/dut-ai-manager-prod/avatars/3_20260419_145653.JPG"
      },
      {
        "id": 4,
        "name": "Ngô Văn Đắc Trí",
        "email": "dactri641@gmail.com",
        "avatar_url": "https://minio.dutai.site/dut-ai-manager-prod/avatars/4_20260124_161828.jpg"
      }
    ]
  }
  ```
- **Observations & Types**:
  - `id` is strictly an integer (`int`): `3`, `4`, etc.
  - `name`: string.
  - `email`: string.
  - `avatar_url`: string or null.

### Endpoint 2: Single User Detail
- **Method & Path**: `GET https://manage.dutai.io.vn/api/v1/users/{id}`
- **Response Format**:
  ```json
  {
    "is_success": true,
    "status_code": 200,
    "data": {
      "id": 1,
      "name": "Huỳnh Phước Nguyên",
      "email": "huynhphuocnguyen.dev@gmail.com",
      "phone_number": "0931960822",
      "status": "ACTIVE",
      "role_ids": [1, 9, 13],
      "role_names": ["admin", "Trainer", "Content"],
      "permissions": ["billing:read", "account:create", ...],
      "avatar_url": "https://minio.dutai.site/...",
      "discord_id": "363660101631868929",
      "zalo_bot_id": "6b3eb58134cadd9484db",
      "check_in_card_code_configured": true
    },
    "message": "Fetched user profile",
    "pagination": null
  }
  ```
- **Observations & Types**:
  - `id` is strictly an integer (`int`): `1`.
  - `role_ids` is a list of integers (`list[int]`).
  - `role_names` and `permissions` are lists of strings.
  - `phone_number` and `avatar_url` are optional strings.

---

## 2. Removal of Local User Database & Credentials

### Decision
- **Local credentials**: Fully eliminated. The platform will NOT store passwords, password hashes, or local user registration tables.
- **Migration**: Drop or obsolete table `users`. Remove `UserModel` from active authentication queries.
- **Local Auth Endpoints**:
  - Deprecate/remove `/api/v1/auth/register` and local password `/api/v1/auth/login`.
  - Expose `/api/v1/auth/sso-login`, `/api/v1/auth/me`, and `/api/v1/auth/logout`.
- **User Directory Endpoints**:
  - `GET /api/v1/users/options` -> proxies/delegates to `manage.dutai.io.vn/api/v1/users/options`.
  - `GET /api/v1/users/{id:int}` -> proxies/delegates to `manage.dutai.io.vn/api/v1/users/{id}`.

---

## 3. Strict Integer Identifier Invariant

### Constraint
The user explicitly stated: *"Nhớ id là int, không là string nhé, không chơi ép kiểu để chấp vá"*.

### Architectural Enforcement
1. **FastAPI Path Parameter**:
   `@router.get("/users/{id}", ...)` with `id: int = Path(..., ge=1, description="User integer identifier")`.
   Any call to `/users/abc` or `/users/none` will be automatically rejected with HTTP 422 by FastAPI validation before executing any handler code.
2. **Domain Entities**:
   `ExternalUserOptionEntity(id: int, ...)`
   `ExternalUserDetailEntity(id: int, ...)`
   `id: int` is strictly typed in pure Python dataclasses.
3. **Pydantic Schemas**:
   All DTOs define `id: int`. No `str` or loose `Any` definitions.
4. **SSO Token Extraction**:
   When reading token payload `sub`:
   ```python
   # JWT 'sub' claim standardizes as string in RFC 7519, convert once to native integer for user identity
   user_id: int = int(payload["sub"])
   ```
   No string concatenation or coercion workarounds.

---

## 4. Upstream HTTP Client & Error Handling Strategy

### Connection Pooling & Resilience
- Use `httpx.AsyncClient` with connection pooling, timeout (10.0s), and explicit exception handling:
  - `httpx.ConnectError` -> `HTTP 502 Bad Gateway` ("Không thể kết nối tới dịch vụ người dùng DUT-AI").
  - `httpx.TimeoutException` -> `HTTP 504 Gateway Timeout` ("Dịch vụ người dùng DUT-AI phản hồi quá lâu").
  - `404 Not Found` from upstream -> `HTTP 404 Not Found` ("Người dùng không tồn tại").
  - `401/403` from upstream -> `HTTP 401 Unauthorized` / `HTTP 403 Forbidden`.
