# Quickstart Validation Guide: Granular Key-Level Permissions

**Feature**: `005-key-level-permissions`  
**Target Duration**: < 5 minutes  

Follow this guide to validate that Vault secrets are filtered strictly by identity-to-key permissions ("ai được get key gì"), without relying on broad roles.

---

## Step 1: Create Project and Two Secrets

```bash
# 1. Create a Project
PROJECT_ID=$(curl -s -X POST "http://localhost:8000/api/v1/gateway/projects" \
  -H "Content-Type: application/json" \
  -d '{"name": "Billing App", "slug": "billing-app"}' | jq -r '.id')

# 2. Add Secret 1: DATABASE_URL
curl -s -X POST "http://localhost:8000/api/v1/vault/projects/$PROJECT_ID/secrets" \
  -H "Content-Type: application/json" \
  -d '{"scope_name": "common", "key": "DATABASE_URL", "value": "postgres://usr:pass@db/main"}'

# 3. Add Secret 2: STRIPE_SECRET_KEY
curl -s -X POST "http://localhost:8000/api/v1/vault/projects/$PROJECT_ID/secrets" \
  -H "Content-Type: application/json" \
  -d '{"scope_name": "payment", "key": "STRIPE_SECRET_KEY", "value": "sk_live_secret_999"}'
```

---

## Step 2: Grant Permissions to Identity `dev_alice`

Grant `dev_alice` access ONLY to `DATABASE_URL`:
```bash
curl -X POST "http://localhost:8000/api/v1/vault/projects/$PROJECT_ID/permissions" \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: admin" \
  -d '{
    "identity_id": "dev_alice",
    "identity_type": "user",
    "secret_key": "DATABASE_URL"
  }'
```

---

## Step 3: Verify Key-Level Secret Filtering

### A. Retrieve Secrets as `dev_alice`
```bash
curl -s "http://localhost:8000/api/v1/vault/projects/$PROJECT_ID/secrets" \
  -H "X-Identity-Id: dev_alice" | jq .
```
**Expected Outcome**:
```json
{
  "project_id": "...",
  "scopes": {
    "common": {
      "DATABASE_URL": "postgres://usr:pass@db/main"
    }
  }
}
```
*(Notice: `STRIPE_SECRET_KEY` is completely absent! Zero leakage).*

### B. Attempt Unauthorized Direct Request
```bash
curl -i "http://localhost:8000/api/v1/vault/projects/$PROJECT_ID/secrets?key=STRIPE_SECRET_KEY" \
  -H "X-Identity-Id: dev_alice"
```
**Expected Outcome**:
`HTTP/1.1 403 Forbidden`  
`{"detail": "Access denied: Identity does not have permission to access secret key 'STRIPE_SECRET_KEY'"}`

---

## Step 4: Grant Permission to `dev_alice` for `STRIPE_SECRET_KEY` and Verify Instant Access

```bash
# Grant access
curl -X POST "http://localhost:8000/api/v1/vault/projects/$PROJECT_ID/permissions" \
  -H "Content-Type: application/json" \
  -d '{
    "identity_id": "dev_alice",
    "identity_type": "user",
    "secret_key": "STRIPE_SECRET_KEY"
  }'

# Read secrets again
curl -s "http://localhost:8000/api/v1/vault/projects/$PROJECT_ID/secrets" \
  -H "X-Identity-Id: dev_alice" | jq .
```
**Expected Outcome**:
Response now immediately includes BOTH `DATABASE_URL` and `STRIPE_SECRET_KEY`.
