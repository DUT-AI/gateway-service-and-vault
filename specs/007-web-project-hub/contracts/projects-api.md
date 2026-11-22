# API Contracts: Web Phase 1 - Project Hub & Core Navigation

**Feature**: `007-web-project-hub`  
**Date**: 2026-11-23  

## 1. List Projects

Retrieve all business projects registered in the gateway and vault platform.

- **URL**: `/api/v1/gateway/projects`
- **Method**: `GET`
- **Headers**:
  - `Cookie: access_token=<sso_token>` OR `Authorization: Bearer <sso_token>`
- **Response 200 OK**:
  ```json
  [
    {
      "id": "01JD27M508E9D0V2V1Z9Q1ABC0",
      "name": "Payment Gateway Core",
      "slug": "payment-gateway-core",
      "description": "Microservice for processing financial transactions",
      "created_at": "2026-11-23T04:20:00Z"
    }
  ]
  ```

---

## 2. Get Project by ID

Retrieve detailed metadata of a specific project.

- **URL**: `/api/v1/gateway/projects/{project_id}`
- **Method**: `GET`
- **Headers**:
  - `Cookie: access_token=<sso_token>` OR `Authorization: Bearer <sso_token>`
- **Response 200 OK**:
  ```json
  {
    "id": "01JD27M508E9D0V2V1Z9Q1ABC0",
    "name": "Payment Gateway Core",
    "slug": "payment-gateway-core",
    "description": "Microservice for processing financial transactions",
    "created_at": "2026-11-23T04:20:00Z"
  }
  ```
- **Response 404 Not Found**:
  ```json
  {
    "detail": "Project 'non_existent_id' not found"
  }
  ```

---

## 3. Create Project

Create a new project workspace.

- **URL**: `/api/v1/gateway/projects`
- **Method**: `POST`
- **Headers**:
  - `Content-Type: application/json`
  - `Cookie: access_token=<sso_token>` OR `Authorization: Bearer <sso_token>`
- **Request Body**:
  ```json
  {
    "name": "E-Commerce Gateway",
    "slug": "e-commerce-gw",
    "description": "Gateway for store services"
  }
  ```
- **Response 201 Created**:
  ```json
  {
    "id": "01JD27M508E9D0V2V1Z9Q1ABC1",
    "name": "E-Commerce Gateway",
    "slug": "e-commerce-gw",
    "description": "Gateway for store services",
    "created_at": "2026-11-23T05:00:00Z"
  }
  ```
- **Response 422 Unprocessable Entity**:
  Returned when payload validation fails (name too short, slug invalid format).

---

## 4. Current User Session

Retrieve current SSO user profile for AppShell header.

- **URL**: `/api/v1/auth/me`
- **Method**: `GET`
- **Headers**:
  - `Cookie: access_token=<sso_token>` OR `Authorization: Bearer <sso_token>`
- **Response 200 OK**:
  ```json
  {
    "id": 1,
    "email": "huynhphuocnguyen.dev@gmail.com",
    "name": "Huỳnh Phước Nguyên",
    "role": "admin",
    "role_names": ["admin", "Trainer"],
    "permissions": ["account:create", "..."],
    "avatar_url": "https://minio.dutai.site/avatars/1.jpg",
    "status": "ACTIVE"
  }
  ```
