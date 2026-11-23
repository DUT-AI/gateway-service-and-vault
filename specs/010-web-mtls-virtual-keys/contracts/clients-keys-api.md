# API Contract: mTLS Clients & Virtual Keys Endpoints

**Feature Branch**: `010-web-mtls-virtual-keys`  
**Date**: 2026-11-23  
**Status**: Authoritative (Matches Backend OpenAPI Specification)  

---

## 1. Clients & Device Management API

### 1.1 List Registered Clients
- **Method**: `GET`
- **Path**: `/api/v1/gateway/clients`
- **Operation ID**: `list_clients_api_v1_gateway_clients_get`
- **Description**: Returns a list of all client devices and workload containers registered in the platform.

#### Request Headers
```http
Accept: application/json
Authorization: Bearer <sso-token> (or cookie-based session)
```

#### Response: `200 OK`
```json
[
  {
    "id": "c7a80b12-4f3a-4938-b7c1-842f1f516801",
    "name": "MacBook Pro M3",
    "client_type": "USER_DEVICE",
    "owner_id": "1",
    "cert_fingerprint": "3a:f1:9c:88:2d:4b:11:e9:04:aa:67:82:1c:ee:91:ff:00:2b:88:31",
    "cert_serial": "1049281729481729481",
    "expires_at": "2026-12-23T06:50:00Z",
    "is_revoked": false,
    "created_at": "2026-11-23T06:50:00Z"
  }
]
```

---

### 1.2 Register Client Device & Issue Certificate
- **Method**: `POST`
- **Path**: `/api/v1/gateway/clients`
- **Operation ID**: `register_client_api_v1_gateway_clients_post`
- **Description**: Creates a new device record, signs an X.509 certificate with the internal CA, and generates an ECC/RSA private key. Returns the certificate bundle.

#### Request Headers & Body
```http
Content-Type: application/json
Accept: application/json
```
```json
{
  "name": "MacBook Pro M3",
  "client_type": "USER_DEVICE",
  "owner_id": "1",
  "validity_days": 90
}
```

#### Response: `201 Created`
```json
{
  "id": "c7a80b12-4f3a-4938-b7c1-842f1f516801",
  "name": "MacBook Pro M3",
  "client_type": "USER_DEVICE",
  "owner_id": "1",
  "cert_fingerprint": "3a:f1:9c:88:2d:4b:11:e9:04:aa:67:82:1c:ee:91:ff:00:2b:88:31",
  "cert_serial": "1049281729481729481",
  "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIBkzCCATqgAwIBAgIU...\n-----END CERTIFICATE-----",
  "key_pem": "-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49...\n-----END PRIVATE KEY-----",
  "expires_at": "2027-02-21T06:50:00Z"
}
```

#### Response: `422 Unprocessable Entity`
Returned when validation constraints fail (e.g., missing name or owner_id).
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 2 characters",
      "input": ""
    }
  ]
}
```

---

## 2. Virtual Keys Management API

### 2.1 List Project Virtual Keys
- **Method**: `GET`
- **Path**: `/api/v1/gateway/projects/{project_id}/keys`
- **Operation ID**: `list_virtual_keys_api_v1_gateway_projects__project_id__keys_get`
- **Description**: Lists all virtual access keys assigned to a given project workspace, including bound client IDs and status.

#### Response: `200 OK`
```json
[
  {
    "id": "9d8e7f6a-5b4c-3d2e-1f0a-b9c8d7e6f5a4",
    "client_id": "c7a80b12-4f3a-4938-b7c1-842f1f516801",
    "project_id": "proj-core-banking-01",
    "key_prefix": "vkey_dev_9a4f",
    "status": "ACTIVE",
    "created_at": "2026-11-23T07:00:00Z",
    "revoked_at": null
  }
]
```

---

### 2.2 Generate Virtual Access Key
- **Method**: `POST`
- **Path**: `/api/v1/gateway/keys`
- **Operation ID**: `generate_virtual_key_api_v1_gateway_keys_post`
- **Description**: Issues a new Virtual Access Key bound 1:1 to the specified client device and project workspace. Returns the full raw token **one time only**.

#### Request Body
```json
{
  "client_id": "c7a80b12-4f3a-4938-b7c1-842f1f516801",
  "project_id": "proj-core-banking-01"
}
```

#### Response: `201 Created`
```json
{
  "id": "9d8e7f6a-5b4c-3d2e-1f0a-b9c8d7e6f5a4",
  "client_id": "c7a80b12-4f3a-4938-b7c1-842f1f516801",
  "project_id": "proj-core-banking-01",
  "virtual_key": "vkey_dev_9a4f8b2c1d3e5f7a0b9c8d7e6f5a4b3c2d1e0f9a",
  "key_prefix": "vkey_dev_9a4f",
  "status": "ACTIVE",
  "created_at": "2026-11-23T07:00:00Z"
}
```

---

### 2.3 Revoke Virtual Access Key
- **Method**: `POST`
- **Path**: `/api/v1/gateway/keys/{key_id}/revoke`
- **Operation ID**: `revoke_virtual_key_api_v1_gateway_keys__key_id__revoke_post`
- **Description**: Revokes the virtual key immediately. The gateway's identity binding filter will instantly reject any request presenting this key with HTTP 403.

#### Path Parameters
- `key_id`: `string` (UUID of the virtual key to revoke)

#### Response: `200 OK`
```json
{
  "message": "Virtual key revoked successfully",
  "key_id": "9d8e7f6a-5b4c-3d2e-1f0a-b9c8d7e6f5a4"
}
```

#### Response: `404 Not Found`
```json
{
  "detail": "Virtual key not found"
}
```
