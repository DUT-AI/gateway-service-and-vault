# Quickstart Validation Guide: Boilerplate Advanced Capabilities

## 1. Outbox Processor Validation
Run the unit test verifying batch event dispatching, handler execution, and failure status handling:
```bash
uv run pytest tests/unit/test_outbox_processor.py -v
```
**Expected Outcome**: All outbox handler scenarios pass with 0 errors.

---

## 2. Paginated List Query Validation
```bash
# Query paginated users
curl -s "http://localhost:8000/api/v1/auth/users?page=1&page_size=5" | jq .
```
**Expected Outcome**: Returns `{ "items": [...], "total": N, "page": 1, "page_size": 5, "total_pages": M }`.

---

## 3. Frontend Web Application Validation
```bash
# Run web server
make dev-web
```
1. Open browser to `http://localhost:3000/dashboard`. Verify automatic redirect to `http://localhost:3000/login`.
2. Enter email and password to log in.
3. Observe automatic redirect to `/dashboard` with user profile displayed.
4. Click "Logout" and verify redirection back to `/login`.

---

## 4. Production Docker Build Validation
```bash
docker build -t boilerplate-api:prod .
```
**Expected Outcome**: Builds multi-stage production image successfully under 200MB.

---

## 5. CI/CD Verification
```bash
# Verify formatting, type checking, tests, and contract drift
make ruff
make check
make test
make api-types
git diff --exit-code web/src/types/api.generated.d.ts
```
**Expected Outcome**: Zero lint errors, zero type errors, 100% passing tests, and no API contract drift.
