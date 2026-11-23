# Quickstart & Verification Guide: Gateway Quota & Rate Limiting (Phase 2)

## Prerequisites
- APISIX container running on ports 9080 (HTTP), 9443 (HTTPS mTLS), 9180 (Admin).
- Redis container running on port 6379/6380.
- FastAPI backend running on port 8000.

---

## Scenario 1: Verify APISIX RPM Rate Limiting Surge (User Story 1)

1. Register an upstream service with `rate_limit_rpm = 5`:
   ```bash
   curl -X POST http://localhost:8000/api/v1/gateway/services \
     -H "Content-Type: application/json" \
     -d '{"name": "Low RPM Svc", "slug": "low-rpm-svc", "base_url": "https://httpbin.org/get", "auth_type": "NONE"}'
   ```
2. Bind service to project with `rate_limit_rpm = 5`.
3. Send 6 requests in rapid succession (< 5s):
   ```bash
   for i in {1..6}; do
     curl -s -o /dev/null -w "%{http_code}\n" -k --cert ~/Downloads/mtls-client.crt --key ~/Downloads/mtls-client.key \
       -H "X-Virtual-Key: <VIRTUAL_KEY>" \
       -H "X-Project-Id: <PROJECT_ID>" \
       https://localhost:9443/services/low-rpm-svc/get
   done
   ```
4. **Expected Output**:
   - First 5 requests: `200`
   - 6th request: `429` (Rate limit exceeded)

---

## Scenario 2: Verify Daily Quota Ceiling & Rejection (User Story 2)

1. Bind service with `quota_daily = 3`:
   ```bash
   curl -X PUT http://localhost:8000/api/v1/gateway/projects/<PROJ_ID>/services/<SVC_ID>/quota \
     -H "Content-Type: application/json" \
     -d '{"rate_limit_rpm": 60, "quota_daily": 3}'
   ```
2. Send 4 requests through the gateway.
3. **Expected Output**:
   - Calls 1 to 3: `200 OK`
   - Call 4: `429 Too Many Requests` (`Daily request quota exceeded`)

---

## Scenario 3: Query Usage API & View UI Progress Bar (User Stories 3 & 4)

1. Query usage API:
   ```bash
   curl http://localhost:8000/api/v1/gateway/projects/<PROJ_ID>/services/<SVC_ID>/usage
   ```
2. Open Web browser at `http://localhost:3000/projects/<PROJ_ID>`.
3. Check "Dịch vụ được phép" table:
   - Progress bar shows `3 / 3 (100.0%)` with a red highlight badge.
