# Quickstart & Verification Guide: Audit Logging & Security Alerts (Phase 3)

**Branch**: `015-audit-logging-security-alerts` | **Date**: 2026-11-23

This guide provides runnable step-by-step instructions to verify that audit logging, security anomaly detection, and the Web UI view operate correctly end-to-end.

---

## 1. Prerequisites

- FastAPI backend running on `http://localhost:8000`
- PostgreSQL running on port 5432
- APISIX gateway running on port 9443 (mTLS) and 9080 (HTTP)
- Next.js Web UI running on `http://localhost:3000`

---

## 2. Test Scenario 1: Automatic Audit Log Recording on Gateway Access

### Step 1.1: Execute a valid mTLS Gateway Call
```bash
curl -k --cert mtls-client.crt --key mtls-client.key \
  -H "X-Virtual-Key: <VALID_VIRTUAL_KEY>" \
  -H "X-Project-Id: <PROJECT_ID>" \
  https://localhost:9443/services/llm/models
```
*Expected Result*: HTTP 200 OK.

### Step 1.2: Execute an invalid (mismatched) mTLS Gateway Call
```bash
# Call with mismatched cert or altered virtual key
curl -k --cert wrong-client.crt --key wrong-client.key \
  -H "X-Virtual-Key: <VALID_VIRTUAL_KEY>" \
  -H "X-Project-Id: <PROJECT_ID>" \
  https://localhost:9443/services/llm/models
```
*Expected Result*: HTTP 403 Forbidden (`IDENTITY_MISMATCH`).

### Step 1.3: Verify Audit Records in Backend API
```bash
curl -s http://localhost:8000/api/v1/gateway/audit-events | jq .
```
*Expected Result*:
- One record with `decision: "ALLOW"`, `action: "GATEWAY_ACCESS"`.
- One record with `decision: "DENY"`, `action: "GATEWAY_ACCESS"`, `error_code: "IDENTITY_MISMATCH"`.

---

## 3. Test Scenario 2: Security Anomaly Detection (Threshold Trigger)

### Step 2.1: Fire 4 consecutive Identity Mismatch requests
```bash
for i in {1..4}; do
  curl -s -k --cert wrong-client.crt --key wrong-client.key \
    -H "X-Virtual-Key: <VALID_VIRTUAL_KEY>" \
    https://localhost:9443/services/llm/models > /dev/null
done
```

### Step 2.2: Query Security Alerts API
```bash
curl -s http://localhost:8000/api/v1/gateway/security-alerts | jq .
```
*Expected Result*:
```json
{
  "alerts": [
    {
      "severity": "HIGH",
      "anomaly_type": "REPEATED_IDENTITY_MISMATCH",
      "event_count": 4
    }
  ],
  "total_active": 1
}
```

---

## 4. Test Scenario 3: Web UI Audit View Verification

1. Open browser to `http://localhost:3000/audit`.
2. Observe the sidebar item **"Nhật ký an ninh"** highlighted with `ShieldAlert` icon.
3. Observe the high-severity alert banner showing active repeated mismatches.
4. Verify table columns:
   - **Thời gian**: Formatted UTC/Local time.
   - **Đối tượng (Actor)**: `User Device` (blue) or `App Server` (purple) badge with Client ID.
   - **Hành động (Action)**: `GATEWAY_ACCESS`.
   - **Kết quả (Decision)**: Green `ALLOW` badge or Red `DENY` badge.
   - **Lý do / Lỗi**: `IDENTITY_MISMATCH`, `DAILY_QUOTA_EXCEEDED`, or `-`.
   - **Chi tiết (Metadata)**: Modal button opening formatted JSON payload.
5. Use filter dropdowns to filter by `Decision = DENY` or `Client Type = USER_DEVICE`.
