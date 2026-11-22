# Quickstart Validation Guide: Modular Monolith Boilerplate

## 1. Prerequisites
- **Python**: `>= 3.12`
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv) `>= 0.4.0`
- **Frontend Runtime**: `Node.js >= 20` and `pnpm >= 9.0`
- **Containers**: `Docker` & `Docker Compose`

---

## 2. Environment Setup

```bash
# 1. Clone repository & configure environment
cp .env.example .env

# 2. Install pre-commit hooks
make install-hooks

# 3. Start backing services (PostgreSQL, Redis, MinIO)
docker compose up -d postgres redis minio

# 4. Install backend dependencies & run database migrations
uv sync
make migrate
```

---

## 3. Running Services Locally

```bash
# Terminal 1: Start FastAPI Backend Server (reload enabled)
make dev-api
# API available at: http://localhost:8000
# OpenAPI Swagger UI: http://localhost:8000/docs

# Terminal 2: Start Next.js Frontend
make dev-web
# Web UI available at: http://localhost:3000

# Terminal 3: Start ARQ Background Worker
make dev-worker
```

---

## 4. End-to-End Validation Steps

### Step 4.1: Validate Clean Architecture Domain Purity Gate
Verify that no domain entity imports Pydantic, FastAPI, or SQLAlchemy:
```bash
uv run pytest tests/test_clean_architecture_purity.py -v
```
**Expected Outcome**: All domain modules pass with `0` violations.

### Step 4.2: Validate Authentication Flow
```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "SuperSecretPassword123!", "name": "Admin User"}'

# Login to receive JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "SuperSecretPassword123!"}'

# Call authenticated endpoint /me with Bearer token
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```
**Expected Outcome**: Returns status `200 OK` with user details matching `UserResponse` schema.

### Step 4.3: Validate Offline Frontend Type Synchronization
```bash
make api-types
```
**Expected Outcome**:
1. `apps/api/openapi_export.py` generates `web/openapi.json` offline without a running server.
2. `web/src/types/api.generated.d.ts` is updated with full TypeScript definitions for `/api/v1/auth/*` endpoints and DTOs.
3. Running `cd web && pnpm typecheck` passes with zero type errors.

### Step 4.4: Code Quality & Linter Checks
```bash
# Format and lint python code
make ruff

# Strict typecheck on backend
make check

# Run full backend test suite
make test
```
**Expected Outcome**: All commands exit with return code `0`.
