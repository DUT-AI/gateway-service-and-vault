# Contracts: Boilerplate Advanced Capabilities

## 1. Paginated Users API Contract
- **Endpoint**: `GET /api/v1/auth/users`
- **Query Parameters**:
  - `page`: integer (default: 1)
  - `page_size`: integer (default: 20)
  - `search`: string (optional)
- **Response**: `PaginatedResponse[UserResponse]`
  ```json
  {
    "items": [
      {
        "id": 1,
        "email": "admin@example.com",
        "name": "Admin",
        "role": "admin",
        "status": "ACTIVE",
        "avatar_url": null,
        "created_at": "2026-11-22T13:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  }
  ```

---

## 2. Frontend Auth Flow & Interceptor Contract
- **Default Base URL**: `http://localhost:8000/api/v1`
- **Credentials**: `withCredentials = true` in Axios requests.
- **401 Interceptor**:
  - If status is `401 Unauthorized` AND URL does not include `/auth/login`:
    - Clears stored auth tokens.
    - Redirects window location to `/login`.
