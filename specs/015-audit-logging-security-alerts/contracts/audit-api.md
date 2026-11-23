# API Contract: Audit Logging & Security Alerts (Phase 3)

**Branch**: `015-audit-logging-security-alerts` | **Date**: 2026-11-23

## Endpoints Summary

| Method | Path | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/gateway/audit-events` | Query, filter, and paginate audit events | SSO Token (Admin / Auditor / Member) |
| `GET` | `/api/v1/gateway/security-alerts` | Retrieve active security anomalies (repeated mismatches) | SSO Token (Admin / Auditor / Member) |

---

## 1. `GET /api/v1/gateway/audit-events`

Query audit log records with filtering and pagination.

### Query Parameters

| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `project_id` | `string` | No | None | Filter by Project ULID |
| `client_type` | `string` | No | None | `USER_DEVICE` or `APP_SERVER` |
| `decision` | `string` | No | None | `ALLOW` or `DENY` |
| `action` | `string` | No | None | e.g. `GATEWAY_ACCESS`, `SSO_LOGIN`, `SECRET_READ` |
| `error_code` | `string` | No | None | e.g. `IDENTITY_MISMATCH`, `DAILY_QUOTA_EXCEEDED` |
| `date_from` | `datetime` | No | None | ISO-8601 start date |
| `date_to` | `datetime` | No | None | ISO-8601 end date |
| `limit` | `integer` | No | 50 | Page size (1 - 100) |
| `offset` | `integer` | No | 0 | Page offset (>= 0) |

### Response `200 OK`

```json
{
  "items": [
    {
      "id": "01M86XYZ1234567890ABCDEFGH",
      "timestamp": "2026-11-23T14:30:00Z",
      "client_type": "USER_DEVICE",
      "actor_id": "01M83VNA448ME128ZYE24MG328",
      "project_id": "01M82RAP4HV21BEH9X3ZF3ASVG",
      "service_id": "01M82XYZ789SERVICE001ABC",
      "action": "GATEWAY_ACCESS",
      "decision": "DENY",
      "client_ip": "172.18.0.1",
      "error_code": "IDENTITY_MISMATCH",
      "metadata": {
        "virtual_key_prefix": "vk_live_5954...",
        "cert_fingerprint": "a1b2c3d4...",
        "expected_fingerprint": "e5f6g7h8..."
      }
    }
  ],
  "total": 142,
  "limit": 50,
  "offset": 0
}
```

---

## 2. `GET /api/v1/gateway/security-alerts`

Returns active security anomalies detected by the platform (e.g. repeated Identity Mismatches indicating key leakage or unauthorized tampering).

### Response `200 OK`

```json
{
  "alerts": [
    {
      "alert_id": "alert_01M87ANOMALY01",
      "severity": "HIGH",
      "anomaly_type": "REPEATED_IDENTITY_MISMATCH",
      "description": "Client 01M83VNA448ME128ZYE24MG328 (IP: 172.18.0.1) triggered 4 Identity Mismatch violations within 5 minutes.",
      "actor_id": "01M83VNA448ME128ZYE24MG328",
      "client_ip": "172.18.0.1",
      "event_count": 4,
      "first_seen_at": "2026-11-23T14:26:12Z",
      "last_seen_at": "2026-11-23T14:29:45Z"
    }
  ],
  "total_active": 1
}
```
