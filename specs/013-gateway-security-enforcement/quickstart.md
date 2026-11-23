# Quickstart Validation Guide: Core Security & Gateway Enforcement

**Feature Branch**: `013-gateway-security-enforcement`

Follow these verification scenarios to validate that Gateway Zero-Trust identity binding and client revocation are functioning properly end-to-end.

---

## Prerequisites

1. Docker infrastructure running:
   ```bash
   docker compose up -d
   ```
2. FastAPI Backend running:
   ```bash
   uv run uvicorn apps.api.main:app --port 8000 --reload
   ```
3. Frontend Next.js running:
   ```bash
   cd web && pnpm dev
   ```

---

## Scenario 1: Rejecting Plaintext HTTP or Missing Virtual Key

Verify that unauthenticated calls to upstream services are rejected by APISIX immediately:

```bash
# 1. Call without X-Virtual-Key or mTLS
curl -i http://localhost:9080/services/llm/models

# Expected Output:
# HTTP/1.1 401 Unauthorized (or 403 Forbidden)
# {"error":"UNAUTHORIZED","message":"Missing X-Virtual-Key header"}
```

```bash
# 2. Call with X-Virtual-Key but without mTLS client certificate over port 9080
curl -i -H "X-Virtual-Key: vk_live_test123" http://localhost:9080/services/llm/models

# Expected Output:
# HTTP/1.1 403 Forbidden
# {"error":"MTLS_REQUIRED","message":"Valid client certificate required"}
```

---

## Scenario 2: Successful Request via mTLS with Bound Virtual Key

Verify that legitimate traffic with valid client certificate and virtual key is forwarded:

```bash
curl -i --cert ~/Downloads/test-client.crt --key ~/Downloads/test-client.key -k \
  -H "X-Virtual-Key: vk_live_603a1d138a610bb8dbd8dda8ceadf07cd4334d1f" \
  -H "X-Project-Id: 01KNQW2G1G0DFEFY42P24446EE" \
  https://localhost:9443/services/llm/models

# Expected Output:
# HTTP/1.1 200 OK
# Content-Type: application/json
# [{"id":"gpt-4o",...}]
```

---

## Scenario 3: Revoking Client Device via API & UI

1. **Via API**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/gateway/clients/{CLIENT_ID}/revoke \
     -H "Authorization: Bearer $SSO_TOKEN"
   
   # Expected Output:
   # {"message":"Client and all associated virtual keys revoked successfully","client_id":"...","is_revoked":true}
   ```

2. **Via Web UI**:
   - Navigate to `http://localhost:3000/clients`.
   - Locate the client row and click "Thu hồi thiết bị".
   - Confirm in the dialog.
   - Verify the status badge switches to red `REVOKED` ("Đã thu hồi").

3. **Re-test with Revoked Device**:
   ```bash
   curl -i --cert ~/Downloads/test-client.crt --key ~/Downloads/test-client.key -k \
     -H "X-Virtual-Key: vk_live_603a1d138a610bb8dbd8dda8ceadf07cd4334d1f" \
     -H "X-Project-Id: 01KNQW2G1G0DFEFY42P24446EE" \
     https://localhost:9443/services/llm/models

   # Expected Output:
   # HTTP/1.1 403 Forbidden
   # {"error":"IDENTITY_MISMATCH","message":"Virtual Access Key is not bound to this client certificate or project"}
   ```
