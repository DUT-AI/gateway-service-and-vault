# API Contract: SSO Authentication & External User Directory

**Base Route**: `/api/v1`

---

## 1. Authentication Endpoints

### A. SSO Login
- **Method**: `POST`
- **Path**: `/api/v1/auth/sso-login`
- **Request Body**:
  ```json
  {
    "email": "user@dutai.io.vn",
    "password": "mypassword"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "token_type": "bearer",
    "expires_in": 604800
  }
  ```
- **Cookies Set**:
  - `access_token`: `<jwt_token>` (HttpOnly, SameSite=Lax)
  - `refresh_token`: `<refresh_token>` (HttpOnly, SameSite=Lax)

---

### B. Current Authenticated Profile
- **Method**: `GET`
- **Path**: `/api/v1/auth/me`
- **Headers**:
  - `Authorization`: `Bearer <token>` (or cookie `access_token`)
- **Response**: `200 OK`
  ```json
  {
    "id": 1,
    "email": "huynhphuocnguyen.dev@gmail.com",
    "name": "Huỳnh Phước Nguyên",
    "role": "admin",
    "avatar_url": "https://minio.dutai.site/...",
    "status": "ACTIVE",
    "role_names": ["admin", "Trainer"],
    "permissions": ["account:read", "billing:read"]
  }
  ```

---

### C. Logout
- **Method**: `POST`
- **Path**: `/api/v1/auth/logout`
- **Response**: `200 OK`
  ```json
  {
    "message": "Đăng xuất thành công"
  }
  ```
- **Cookies Cleared**: `access_token`, `refresh_token`.

---

## 2. External User Directory Endpoints

### A. Get All Users Options
- **Method**: `GET`
- **Path**: `/api/v1/users/options`
- **Headers**:
  - `Authorization`: `Bearer <token>` (or cookie `access_token`)
- **Response**: `200 OK`
  ```json
  [
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
  ```

---

### B. Get User Detail by Integer ID
- **Method**: `GET`
- **Path**: `/api/v1/users/{id}`
- **Path Parameters**:
  - `id`: `integer` (required, strictly $\ge 1$)
- **Headers**:
  - `Authorization`: `Bearer <token>` (or cookie `access_token`)
- **Response**: `200 OK`
  ```json
  {
    "id": 1,
    "name": "Huỳnh Phước Nguyên",
    "email": "huynhphuocnguyen.dev@gmail.com",
    "phone_number": "0931960822",
    "status": "ACTIVE",
    "role_ids": [1, 9, 13],
    "role_names": ["admin", "Trainer", "Content"],
    "permissions": ["billing:read", "account:create"],
    "avatar_url": "https://minio.dutai.site/...",
    "discord_id": "363660101631868929",
    "zalo_bot_id": "6b3eb58134cadd9484db",
    "check_in_card_code_configured": true
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: Token missing or invalid
  - `404 Not Found`: User with given integer ID does not exist in central directory
  - `422 Unprocessable Entity`: ID is not an integer (e.g. `/api/v1/users/abc`)
