# API & Contract Specifications: Core Security & Gateway Enforcement

**Feature Branch**: `013-gateway-security-enforcement`

---

## 1. APISIX to Control Plane Ingress Contract

### `POST /api/v1/gateway/verify-binding`

Invoked synchronously by APISIX custom Lua plugin `identity-binding-filter` prior to upstream forwarding.

#### Request Body Schema (`VerifyBindingRequest`)
```json
{
  "raw_virtual_key": "vk_live_603a1d138a610bb8dbd8dda8ceadf07cd4334d1f",
  "cert_fingerprint": "c8d67dec733fb774f2b315f0c1b76363295b7d7cd8fa0e72cf857d0a8b5328f2",
  "project_id": "01JM8CXYZ00000000000000000",
  "service_slug": "llm"
}
```

#### Successful Response (`200 OK`)
```json
{
  "valid": true,
  "message": "Identity binding verified successfully"
}
```

#### Error Responses
- **403 Forbidden (`IDENTITY_MISMATCH`)**:
  ```json
  {
    "detail": "Client certificate does not match the virtual key binding"
  }
  ```
  *(or `"Client is not found or revoked"`, `"Virtual key does not belong to requested project"`)*
- **403 Forbidden (`SERVICE_NOT_PERMITTED`)**:
  ```json
  {
    "detail": "Upstream service 'llm' is not permitted for project '01JM8CXYZ00000000000000000'"
  }
  ```

---

## 2. Client Device Revocation Endpoint

### `POST /api/v1/gateway/clients/{client_id}/revoke`

Revokes a registered client hardware device and invalidates all active virtual keys bound to this client.

#### Authentication
- Requires Bearer token or valid SSO session cookie.

#### Parameters
- `client_id` (Path, string, ULID): Identifier of the client to revoke.

#### Response (`200 OK`)
```json
{
  "message": "Client and all associated virtual keys revoked successfully",
  "client_id": "01JMBCLIENT000000000000000",
  "is_revoked": true
}
```

#### Error Responses
- **404 Not Found**:
  ```json
  {
    "detail": "Client '01JMBCLIENT000000000000000' not found"
  }
  ```
- **400 Bad Request**:
  ```json
  {
    "detail": "Client '01JMBCLIENT000000000000000' is already revoked"
  }
  ```

---

## 3. APISIX Upstream Route Schema Definition

When `sync_upstream_service_route` provisions a route in APISIX:

```json
{
  "name": "route_llm",
  "uri": "/services/llm/*",
  "plugins": {
    "proxy-rewrite": {
      "regex_uri": ["^/services/llm/(.*)", "/v1/$1"],
      "headers": {
        "Authorization": "Bearer <UPSTREAM_TOKEN>"
      }
    },
    "identity-binding-filter": {
      "control_plane_url": "http://api:8000/api/v1/gateway/verify-binding"
    }
  },
  "upstream": {
    "type": "roundrobin",
    "scheme": "https",
    "nodes": {
      "llm2.dutai.site:443": 1
    },
    "pass_host": "node"
  }
}
```
