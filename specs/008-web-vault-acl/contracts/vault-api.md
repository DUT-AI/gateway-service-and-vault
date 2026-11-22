# API Contracts: Web Phase 2 - Dynamic Vault Management & Key-Level ACL

**Feature**: `008-web-vault-acl`  
**Date**: 2026-11-23  

## 1. List Secret Scopes
Retrieve all secret scopes created within a project.

- **URL**: `/api/v1/vault/projects/{project_id}/scopes`
- **Method**: `GET`
- **Headers**:
  - `Cookie: access_token=<sso_token>` OR `Authorization: Bearer <sso_token>`
- **Response 200 OK**:
  ```json
  [
    {
      "id": "01JD27M508E9D0V2V1Z9Q1SCOPE1",
      "project_id": "01JD27M508E9D0V2V1Z9Q1ABC0",
      "name": "Common",
      "description": "Shared project configurations",
      "created_at": "2026-11-23T04:20:00Z"
    },
    {
      "id": "01JD27M508E9D0V2V1Z9Q1SCOPE2",
      "project_id": "01JD27M508E9D0V2V1Z9Q1ABC0",
      "name": "Database",
      "description": "Database connection credentials",
      "created_at": "2026-11-23T04:21:00Z"
    }
  ]
  ```

---

## 2. Get Decrypted Secrets
Retrieve decrypted configuration secrets filtered by caller permissions and optional scope/key.

- **URL**: `/api/v1/vault/projects/{project_id}/secrets`
- **Method**: `GET`
- **Query Parameters**:
  - `scope` (optional): Filter secrets by specific scope name.
  - `key` (optional): Filter by exact secret key.
- **Headers**:
  - `Cookie: access_token=<sso_token>` OR `Authorization: Bearer <sso_token>`
  - `X-Identity-Id`: (Optional) Identity ID for ACL filtering.
- **Response 200 OK**:
  ```json
  {
    "project_id": "01JD27M508E9D0V2V1Z9Q1ABC0",
    "scopes": {
      "Common": {
        "APP_ENV": "production",
        "LOG_LEVEL": "info"
      },
      "Database": {
        "DB_HOST": "postgres.internal",
        "DB_PORT": "5432",
        "DB_PASSWORD": "supersecretpassword"
      }
    }
  }
  ```

---

## 3. Create or Update Secret
Encrypt with AES-256-GCM and store a secret key-value pair under a scope.

- **URL**: `/api/v1/vault/projects/{project_id}/secrets`
- **Method**: `POST`
- **Headers**:
  - `Content-Type: application/json`
  - `Cookie: access_token=<sso_token>` OR `Authorization: Bearer <sso_token>`
  - `X-Actor-Id`: Email or user ID of the caller performing the update.
- **Request Body**:
  ```json
  {
    "scope_name": "Database",
    "key": "DB_PASSWORD",
    "value": "supersecretpassword"
  }
  ```
- **Response 201 Created**:
  ```json
  {
    "id": "01JD27M508E9D0V2V1Z9Q1SEC01",
    "project_id": "01JD27M508E9D0V2V1Z9Q1ABC0",
    "scope_id": "01JD27M508E9D0V2V1Z9Q1SCOPE2",
    "key": "DB_PASSWORD",
    "version": 1,
    "created_at": "2026-11-23T06:00:00Z"
  }
  ```

---

## 4. List Identity Permissions
List all permitted secret keys for a given user or client identity in a project.

- **URL**: `/api/v1/vault/projects/{project_id}/permissions`
- **Method**: `GET`
- **Query Parameters**:
  - `identity_id`: Identifier of the user or client (e.g. `"1"` for user ID 1).
- **Response 200 OK**:
  ```json
  {
    "project_id": "01JD27M508E9D0V2V1Z9Q1ABC0",
    "identity_id": "1",
    "permitted_keys": [
      "APP_ENV",
      "DB_HOST"
    ]
  }
  ```

---

## 5. Grant Key Permission
Grant an identity permission to read a specific secret key.

- **URL**: `/api/v1/vault/projects/{project_id}/permissions`
- **Method**: `POST`
- **Headers**:
  - `Content-Type: application/json`
  - `X-Actor-Id`: Admin identity ID granting permission.
- **Request Body**:
  ```json
  {
    "identity_id": "1",
    "identity_type": "user",
    "secret_key": "DB_PASSWORD"
  }
  ```
- **Response 201 Created**:
  ```json
  {
    "id": "01JD27M508E9D0V2V1Z9Q1PERM01",
    "project_id": "01JD27M508E9D0V2V1Z9Q1ABC0",
    "identity_id": "1",
    "identity_type": "user",
    "secret_key": "DB_PASSWORD",
    "granted_by": "admin",
    "created_at": "2026-11-23T06:10:00Z"
  }
  ```

---

## 6. Revoke Key Permission
Revoke an identity's access to a specific secret key.

- **URL**: `/api/v1/vault/projects/{project_id}/permissions`
- **Method**: `DELETE`
- **Query Parameters**:
  - `identity_id`: Identity identifier (e.g. `"1"`).
  - `secret_key`: Key to revoke (e.g. `"DB_PASSWORD"`).
- **Response 204 No Content**

---

## 7. Get Central User Options
Fetch directory users for dropdown selection in the ACL modal.

- **URL**: `/api/v1/users/options`
- **Method**: `GET`
- **Response 200 OK**:
  ```json
  [
    {
      "id": 1,
      "name": "Nguyễn Phước Huynh",
      "email": "huynhphuocnguyen.dev@gmail.com",
      "avatar_url": "https://avatars.githubusercontent.com/u/1"
    }
  ]
  ```
