# API Contract: Upstream Services Management Endpoints

**Feature Branch**: `011-web-upstream-services`  
**Date**: 2026-11-23  
**Status**: Authoritative (Matches Backend OpenAPI Specification)  

---

## 1. List Upstream Services
- **Method**: `GET`
- **Path**: `/api/v1/gateway/services`
- **Operation ID**: `list_upstream_services_api_v1_gateway_services_get`
- **Description**: Returns all upstream 3rd-party integration services managed by the Gateway.

### Request Headers
```http
Accept: application/json
Authorization: Bearer <sso-token> (or cookie-based session)
```

### Response: `200 OK`
```json
[
  {
    "id": "e4f8d21b-7a3c-42b1-91a0-384950b71942",
    "name": "OpenAI API Platform",
    "slug": "openai-api-platform",
    "base_url": "https://api.openai.com/v1",
    "auth_type": "BEARER_TOKEN",
    "timeout_seconds": 60,
    "is_active": true,
    "created_at": "2026-11-23T08:30:00Z"
  },
  {
    "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "name": "VNPay Payment Gateway",
    "slug": "vnpay-payment-gateway",
    "base_url": "https://sandbox.vnpayment.vn/paymentv2",
    "auth_type": "API_KEY",
    "timeout_seconds": 30,
    "is_active": true,
    "created_at": "2026-11-23T08:35:00Z"
  }
]
```

---

## 2. Create Upstream Service & Vault Credential
- **Method**: `POST`
- **Path**: `/api/v1/gateway/services`
- **Operation ID**: `create_upstream_service_api_v1_gateway_services_post`
- **Description**: Registers a new upstream partner service. The raw credential is encrypted with AES-256-GCM before storage.

### Request Headers & Body
```http
Content-Type: application/json
Accept: application/json
```
```json
{
  "name": "OpenAI API Platform",
  "slug": "openai-api-platform",
  "base_url": "https://api.openai.com/v1",
  "auth_type": "BEARER_TOKEN",
  "credential": "sk-proj-sample-token-123",
  "timeout_seconds": 60
}
```

### Response: `201 Created`
```json
{
  "id": "e4f8d21b-7a3c-42b1-91a0-384950b71942",
  "name": "OpenAI API Platform",
  "slug": "openai-api-platform",
  "base_url": "https://api.openai.com/v1",
  "auth_type": "BEARER_TOKEN",
  "timeout_seconds": 60,
  "is_active": true,
  "created_at": "2026-11-23T08:30:00Z"
}
```

### Response: `422 Unprocessable Entity`
Returned when validation constraints fail (e.g. invalid URL or missing credential).
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "credential"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```
