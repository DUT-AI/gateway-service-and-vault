# Phase 0 Research & Technical Decisions: Gateway Service & Dynamic Vault

## Overview
This document records the foundational research, technical evaluations, and architectural decisions made for the **Secure API Gateway & Centralized Dynamic Vault Platform**.

---

## Decision 1: Gateway Data Plane Engine (Apache APISIX)

### Decision
Deploy **Apache APISIX 3.9+** (backed by an `etcd 3.5` key-value cluster) as the core API Gateway data plane proxy.

### Rationale
- **High Throughput & Low Latency**: Built on NGINX and OpenResty LuaJIT, APISIX handles tens of thousands of concurrent connections with sub-millisecond proxy latency, meeting our NFR requirement of `< 20ms` p95 overhead.
- **Native Dynamic Configuration (Admin API)**: APISIX does not require reloading NGINX workers when routes, upstreams, SSL certificates, or consumers change. It continuously watches etcd changes and updates routing tables in shared memory in real time.
- **Built-in Plugin Ecosystem**:
  - `proxy-rewrite`: Automatically strips virtual keys and injects real upstream authorization headers (`Authorization: Bearer <token>`, `X-API-KEY: <key>`).
  - `limit-count`: Enforces atomic request rate limits across distributed nodes via Redis.
  - Native mTLS termination: Inspects client x509 certificates and extracts subject DN, serial numbers, and SHA-256 fingerprints directly into NGINX variables (`$ssl_client_fingerprint`).
- **Seamless Custom Plugin Interface**: Adding custom Lua plugins (`identity-binding-filter`) requires fewer than 50 lines of code.

### Alternatives Considered
- **Kong Gateway (Community)**: Feature-rich, but enterprise features (advanced RBAC, granular mTLS mapping) are gated behind proprietary licenses; declarative config reloads can be slower than APISIX etcd sync.
- **Envoy Proxy**: Excellent performance and cloud-native standards, but requires building a custom xDS gRPC control plane service, introducing unnecessary development overhead.
- **Custom Python FastAPI Reverse Proxy**: Unacceptable performance bottlenecks under high concurrency; GIL limits throughput, and handling mTLS renegotiation/forwarding in Python is inefficient.

---

## Decision 2: Identity Binding & Cryptographic Verification Strategy

### Decision
Enforce **Identity Binding** directly inside APISIX via a custom Lua filter (`identity-binding-filter`) paired with Redis caching:
1. Client connects via mTLS presenting its x509 certificate and passes header `X-Virtual-Key: <key>`.
2. APISIX terminates mTLS and extracts `$ssl_client_fingerprint` (SHA-256 fingerprint of the client certificate).
3. The custom Lua filter queries Redis key `vk:<virtual_key>`:
   ```json
   {
     "client_id": "client_01JXYZ...",
     "cert_fingerprint": "a8f5c9...",
     "project_id": "proj_01JABC...",
     "status": "active"
   }
   ```
4. If the fingerprint in the certificate does not strictly match `cert_fingerprint` or the requested route does not match `project_id`, APISIX rejects the request with `HTTP 403 Forbidden` (`{"error": "Identity mismatch: Virtual key is not bound to this client certificate"}`).
5. Successful validations cache the result in APISIX local memory for 60 seconds (with immediate invalidation via Redis Pub/Sub on key revocation).

### Rationale
- Zero additional network hops to backend application servers for auth verification.
- Fast, deterministic rejection: Stolen keys used on another machine are blocked at the edge proxy layer.

### Alternatives Considered
- **FastAPI Auth Forwarding (`forward-auth`)**: Passing every request to FastAPI introduces a 2x latency penalty (~15-30ms per request) and overwhelms the backend during traffic bursts.

---

## Decision 3: Secret Encryption & Storage Scheme (Vault)

### Decision
Adopt **AES-256-GCM (Galois/Counter Mode)** authenticated encryption for all secrets at rest within the PostgreSQL database:
- Master Key: 256-bit cryptographic key supplied via environment variable `VAULT_MASTER_KEY` (or mounted secret).
- Key Derivation: Salted **HKDF (HMAC-based Key Derivation Function)** with SHA-256 derives unique scope/project-level encryption keys.
- Storage Format:
  ```json
  {
    "ciphertext": "<base64_encoded_encrypted_bytes>",
    "nonce": "<base64_encoded_12_byte_iv>",
    "tag": "<base64_encoded_16_byte_auth_tag>",
    "version": 1
  }
  ```
- Access Control: Enforce Role-Based Access Control (RBAC) mapped from DUT AI Manage user tokens:
  - Role `Finance` -> Allowed scopes `Common`, `Financial`.
  - Role `Developer` -> Allowed scope `Common`.

### Rationale
- Authenticated encryption (AEAD) ensures both confidentiality and integrity; ciphertext tampering is detected immediately during decryption.
- Leverages the robust, FIPS-compliant OpenSSL backend via Python's standard `cryptography` library.

### Alternatives Considered
- **Fernet (AES-128-CBC + HMAC-SHA256)**: Secure, but fixed to 128-bit key length and lacks modern hardware AES-NI GCM acceleration.
- **External HashiCorp Vault Server**: Adds an extra heavyweight stateful service to operate and monitor. Database-backed AES-256-GCM satisfies 100% of the project requirements with zero extra operational overhead.

---

## Decision 4: Real-Time In-Memory Hot-Reload Protocol (Zero `.env` on Disk)

### Decision
Combine **Redis Pub/Sub** on the server with **Server-Sent Events (SSE)** over HTTP to stream configuration updates to client application runtimes:
1. When an Administrator modifies a secret in the Control Plane:
   - Database saves the encrypted secret and records an audit log.
   - Control Plane publishes a notification event to Redis channel `project:{id}:secrets_changed`.
2. Connected SDK clients maintain a persistent HTTP connection to `GET /api/v1/vault/live-updates?project_id=...`.
3. The server forwards the event over SSE:
   ```text
   event: secret_update
   data: {"scope": "Financial", "keys": ["PAYMENT_GATEWAY_KEY"], "version": 4}
   ```
4. The client SDK queries the decrypted values over HTTPS and atomically swaps the in-memory configuration dictionary without writing any file to disk or restarting the process.

### Rationale
- Server-Sent Events (SSE) runs over standard HTTP/1.1 or HTTP/2, automatically reconnects, is firewall-friendly, and requires no duplex socket overhead compared to WebSockets.
- Total propagation time from Admin save to process RAM update is `< 2 seconds` (well within the `< 5s` requirement).

### Alternatives Considered
- **HTTP Polling (e.g., every 30 seconds)**: Creates unnecessary server load and introduces up to 30 seconds of configuration drift latency.
- **WebSocket Protocol**: Unnecessary complexity and connection state management for unidirectional server-to-client notifications.
- **Disk-based `.env` synchronization**: Directly violates the core security mandate (zero plaintext secrets on developer disks).

---

## Decision 5: Internal Private CA & Machine Identity Architecture

### Decision
Implement an internal x509 Certificate Authority within `core/security/ca.py` utilizing `cryptography.x509`:
- Root CA: Self-signed 4096-bit RSA / ECDSA P-256 certificate stored securely in the Control Plane.
- Client Certificates:
  - **User Device (Developer)**: Issued with Subject CN `user:<user_id>:<device_id>`, valid for 30 days. Generated upon successful SSO login on DUT AI Manage.
  - **App Server (Docker Workload)**: Issued with Subject CN `app:<service_name>:<deployment_id>`, valid for 90 days. Injected into container environments via volume mounts or orchestration secrets.
- Verification: APISIX trusts the Root CA and strictly validates client certificate chains during TLS handshakes.

### Rationale
- Completely self-contained within the platform; no dependency on third-party public PKI or manual Let's Encrypt DNS challenges.
- Easy rotation and instant revocation via Redis CRL/fingerprint blocklists.
