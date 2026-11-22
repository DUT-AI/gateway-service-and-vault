# Gateway Interface & Proxy Contracts

This document formalizes the interface contracts for the **API Gateway Data Plane (Apache APISIX)** and its integration with the **Control Plane (`modules/gateway`)**.

---

## 1. Gateway Client Request Contract

Clients call upstream services by sending requests to the APISIX Gateway entrypoint (`https://gateway.internal:9443` or `http://localhost:9080`).

### Headers Required:
- `X-Virtual-Key`: The virtual access key issued to the client (e.g. `vk_live_01JXYZ...`).
- Mutual TLS (mTLS): Client must present a valid client certificate issued by the platform root CA.

```http
GET /services/{service_slug}/api/v1/resource HTTP/1.1
Host: gateway.internal:9443
X-Virtual-Key: vk_live_7a8b9c0d1e2f3g4h5i6j
[Client TLS Certificate in Handshake]
```

---

## 2. APISIX Upstream Injection Contract

When APISIX passes verification (mTLS valid, Identity Binding matched in Redis, Quota permitted), it rewrites the request before dispatching to the real upstream service:

1. Strips header `X-Virtual-Key`.
2. Injects upstream credentials configured in `UpstreamService`:
   - `Authorization: Bearer <real_upstream_token>` (for `BEARER_TOKEN`)
   - `X-API-KEY: <real_api_key>` (for `API_KEY`)
3. Forwards path: `/services/{service_slug}/*` -> `{upstream_base_url}/*`.

---

## 3. APISIX Error Response Specifications

### 3.1. Identity Mismatch (Key copied to another machine or project)
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "error": "IDENTITY_MISMATCH",
  "message": "The provided Virtual Access Key is not bound to this client certificate or project."
}
```

### 3.2. Service Not Permitted (Service Scoping violation)
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "error": "SERVICE_NOT_PERMITTED",
  "message": "Project does not have authorization to call upstream service 'payment-core'."
}
```

### 3.3. Rate Limit / Quota Exceeded
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 42

{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Request velocity limit (RPM) exceeded for this service.",
  "retry_after_seconds": 42
}
```

### 3.4. Fail-Closed Control Plane Outage
```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json

{
  "error": "GATEWAY_FAIL_CLOSED",
  "message": "Security control plane is unreachable. Requests rejected under fail-closed security policy."
}
```

---

## 4. Control Plane to APISIX Admin API Contract

The FastAPI backend synchronizes state directly to APISIX via its REST API:

- `PUT /apisix/admin/routes/{service_slug}`:
  ```json
  {
    "uri": "/services/" + service_slug + "/*",
    "plugins": {
      "proxy-rewrite": {
        "regex_uri": ["^/services/" + service_slug + "/(.*)", "/$1"],
        "headers": {
          "Authorization": "Bearer " + decrypted_upstream_token
        }
      },
      "identity-binding-filter": {
        "redis_host": "redis",
        "redis_port": 6379
      },
      "limit-count": {
        "count": 60,
        "time_window": 60,
        "rejected_code": 429,
        "key": "remote_addr",
        "policy": "redis",
        "redis_host": "redis",
        "redis_port": 6379
      }
    },
    "upstream": {
      "type": "roundrobin",
      "nodes": {
        "upstream_host:port": 1
      }
    }
  }
  ```
