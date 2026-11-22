# Quickstart & Verification Guide: Phase 0 Foundation

This document provides step-by-step instructions to set up, initialize, and verify the **Phase 0 Foundation** infrastructure and data models for the Gateway Service & Dynamic Vault platform.

---

## 1. Prerequisites

- Docker & Docker Compose (`docker compose version` >= 2.20)
- Python 3.12+ and `uv` (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- OpenSSL (for verifying client certificates)

---

## 2. Step-by-Step Foundation Setup

### Step 1: Clone & Configure Environment
```bash
# Navigate to repository root
cd /Users/nguyenhuynh/Documents/projects/gateway-service-and-vault

# Verify .env exists or copy example
cp -n .env.example .env
```

### Step 2: Spin Up Infrastructure (PostgreSQL, Redis, MinIO, etcd, APISIX)
```bash
# Start all infrastructure backing services
docker compose up -d postgres redis minio etcd apisix

# Verify container health
docker compose ps
```
*Expected*: All services show `healthy` or `running`.

### Step 3: Run Database Migrations
```bash
# Sync Python dependencies
uv sync

# Apply database migrations for Phase 0 tables
make migrate
```
*Expected*: Tables `projects`, `upstream_services`, `registered_clients`, `virtual_access_keys`, `secret_scopes`, `secrets`, `audit_events` created in PostgreSQL.

---

## 3. End-to-End Verification Scenarios

### Scenario 1: Verify APISIX Gateway Connectivity
```bash
# Check APISIX Admin API health
curl -s http://localhost:9180/apisix/admin/routes -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1'
```
*Expected Output*: `{"action":"get","node":{"key":"/apisix/routes","dir":true,...}}`.

### Scenario 2: Register a Sample Upstream Route in APISIX via Control Plane
```bash
# Call Control Plane API to register mock upstream service
curl -X POST http://localhost:8000/api/v1/gateway/services \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mock AI Service",
    "slug": "ai-service",
    "base_url": "https://httpbin.org",
    "auth_type": "BEARER_TOKEN",
    "credential": "test-real-upstream-token-12345"
  }'
```
*Expected Output*: Returns `HTTP 201 Created`. Route is auto-synced to APISIX.

### Scenario 3: Verify In-Memory Vault Secret Encryption
```bash
# Create a test secret in Scope 'Financial'
curl -X POST http://localhost:8000/api/v1/vault/projects/proj_demo/secrets \
  -H "Content-Type: application/json" \
  -d '{
    "scope_name": "Financial",
    "key": "PAYMENT_KEY",
    "value": "super-secret-bank-key-999"
  }'

# Inspect PostgreSQL raw table to verify encryption at rest
docker compose exec postgres psql -U postgres -d app_db -c "SELECT key, encrypted_value, nonce, auth_tag FROM secrets WHERE key = 'PAYMENT_KEY';"
```
*Expected Output*: `encrypted_value` is base64 ciphertext; plaintext `super-secret-bank-key-999` is NEVER visible in the database.

### Scenario 4: Test Real-Time SSE Hot-Reload Stream
```bash
# Open SSE stream in a terminal
curl -N -H "Accept: text/event-stream" http://localhost:8000/api/v1/vault/projects/proj_demo/stream
```
*In another terminal, update the secret*:
```bash
curl -X POST http://localhost:8000/api/v1/vault/projects/proj_demo/secrets \
  -H "Content-Type: application/json" \
  -d '{
    "scope_name": "Financial",
    "key": "PAYMENT_KEY",
    "value": "super-secret-bank-key-rotated"
  }'
```
*Expected Output*: Terminal 1 immediately prints `event: secret_update` within < 1 second.
