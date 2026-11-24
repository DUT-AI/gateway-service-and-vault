# Quickstart: Pure SSO Authentication & Gateway Verification Guide

## Purpose
Validates the end-to-end Pure SSO authentication flow through the APISIX Zero-Trust Gateway, verifying that browser requests never fail with `405 Method Not Allowed` or `Network Error`.

## Prerequisites
1. Docker Compose running APISIX, etcd, Redis, and PostgreSQL:
   ```bash
   docker compose up -d
   ```
2. Backend API running:
   ```bash
   uv run python -m apps.api.main
   ```
3. Frontend web app running on port 3000:
   ```bash
   cd web && pnpm dev
   ```

## Test Scenarios

### Scenario 1: Verify APISIX Gateway Handles CORS Preflight
Send an `OPTIONS` preflight request through the gateway:
```bash
curl -i -X OPTIONS http://localhost:9080/api/v1/auth/sso-login \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization"
```
**Expected Outcome**:
- Status: `HTTP/1.1 200 OK` (NOT 405 Method Not Allowed)
- Header `Access-Control-Allow-Origin: http://localhost:3000`
- Header `Access-Control-Allow-Credentials: true`

### Scenario 2: Authenticate via SSO Login
Send credential verification request through gateway proxy:
```bash
curl -i -X POST http://localhost:9080/api/v1/auth/sso-login \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d '{"email": "huynhphuocnguyen.dev@gmail.com", "password": "SamplePassword123!"}'
```
**Expected Outcome**:
- Status: `HTTP/1.1 200 OK` (when valid credentials) or `401 Unauthorized` with JSON error detail.
- Response contains `{ "access_token": "...", "token_type": "bearer", "expires_in": 1800 }`.

### Scenario 3: Verify Profile Hydration (/auth/me)
Send profile inspection request with token:
```bash
curl -i http://localhost:9080/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```
**Expected Outcome**:
- Status: `HTTP/1.1 200 OK`
- Returns user profile with native integer `id`, roles, and permissions.

### Scenario 4: Web Browser End-to-End
1. Open `http://localhost:3000/login`.
2. Enter DUT-AI credentials.
3. Click **Đăng nhập SSO DUT-AI**.
4. Browser redirects smoothly to `http://localhost:3000/dashboard` without network error alerts.
