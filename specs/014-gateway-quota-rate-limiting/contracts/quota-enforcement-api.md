# API Contracts: Gateway Quota & Rate Limiting (Phase 2)

## Endpoints

### 1. Query Service Quota Usage
**Endpoint**: `GET /api/v1/gateway/projects/{project_id}/services/{service_id}/usage`

**Success Response**: `200 OK`
```json
{
  "project_id": "01M82RAP4HV21BEH9X3ZF3ASVG",
  "service_id": "01M82XYZ...",
  "usage_today": 2450,
  "quota_daily": 10000,
  "rate_limit_rpm": 60,
  "usage_percentage": 24.5,
  "is_exhausted": false
}
```

---

### 2. Verify Binding (Enriched with Quota Check)
**Endpoint**: `POST /api/v1/gateway/verify-binding`

**Request Body**:
```json
{
  "raw_virtual_key": "vk_live_...",
  "cert_fingerprint": "...",
  "client_raw_cert": "...",
  "project_id": "01M82RAP4HV21BEH9X3ZF3ASVG",
  "service_slug": "llm"
}
```

**Quota Exceeded Error Response**: `429 Too Many Requests`
```json
{
  "code": "DAILY_QUOTA_EXCEEDED",
  "message": "Daily request quota exceeded for this service (limit: 10000)",
  "details": {
    "usage_today": 10001,
    "quota_daily": 10000,
    "retry_after_seconds": 26400
  }
}
```

---

### 3. APISIX `limit-count` Rate Limit Rejection
**Status**: `429 Too Many Requests`
**Headers**:
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 42
Content-Type: text/plain; charset=utf-8
```
**Body**:
```json
{"error_msg":"requests per minute exceeded"}
```
