# API Contracts: Dev Device Self-Registration & Project Key Binding

**Feature**: `021-dev-device-project-binding` | **Date**: 2026-11-25

## 1. `GET /api/v1/gateway/clients`
- **Auth**: `ADMIN`, `PROJECT_DEVELOPER`, or `OTHER`.
- **Behavior**:
  - `ADMIN`: All clients.
  - `PROJECT_DEVELOPER` & `OTHER`: Only clients where `owner_id == str(user_ctx.user_id)`.

## 2. `POST /api/v1/gateway/clients`
- **Auth**: `ADMIN`, `PROJECT_DEVELOPER`, or `OTHER`.
- **Behavior**:
  - `owner_id` always locked to `str(user_ctx.user_id)`.
  - `OTHER`: Only `USER_DEVICE` allowed (`APP_SERVER` returns `HTTP 403 Forbidden`).

## 3. `GET /api/v1/gateway/projects/{project_id}/available-clients`
- **Auth**: `ADMIN` or `PROJECT_DEVELOPER` (must be member of `project_id`; `OTHER` returns `403`).
- **Response `200 OK`**: `list[ClientSummaryResponse]` — Active (non-revoked, non-expired) clients owned by members of `project_id` (or all active clients for `ADMIN`).

## 4. `GET /api/v1/gateway/projects/{project_id}/keys`
- **Auth**: Any authenticated project member (`ADMIN`, `PROJECT_DEVELOPER`, or `OTHER`).
- **Behavior**:
  - `ADMIN` & `PROJECT_DEVELOPER`: All Virtual Keys of `project_id`.
  - `OTHER`: Only Virtual Keys bound to clients owned by `str(user_ctx.user_id)`.
