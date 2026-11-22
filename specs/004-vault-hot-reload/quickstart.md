# Quickstart Validation Guide: Real-Time Dynamic Vault Hot-Reload

**Feature**: `004-vault-hot-reload`  
**Target Duration**: < 5 minutes  

Follow this guide to validate end-to-end event broadcasting, FastAPI SSE streaming, and in-memory SDK hot-reload in under 5 seconds.

---

## Prerequisites

1. Running backend infrastructure containers:
   ```bash
   docker compose ps
   ```
   *Expected*: `boilerplate-postgres`, `boilerplate-redis`, `boilerplate-api` running and healthy.
2. Verified database schema:
   ```bash
   uv run alembic current
   ```

---

## Scenario 1: Validate Server-Sent Events (SSE) Stream

### Step 1.1: Start the SSE Stream Listener
In a dedicated terminal, connect `curl` to the SSE stream endpoint for project `test-proj`:
```bash
curl -N -v -H "Accept: text/event-stream" \
     -H "X-User-Role: admin" \
     "http://localhost:8000/api/v1/vault/projects/test-proj/stream"
```

### Expected Output:
```text
< HTTP/1.1 200 OK
< Content-Type: text/event-stream; charset=utf-8
< Cache-Control: no-cache, no-transform
< Connection: keep-alive

event: connected
data: {"project_id": "test-proj", "status": "active"}

event: ping
data: {"timestamp": "..."}
```

---

## Scenario 2: Validate Real-Time Broadcast on Secret Mutation (< 1s)

### Step 2.1: Publish a Secret Update via Control Plane API
In a second terminal, create or update a secret under `test-proj`:
```bash
curl -X POST "http://localhost:8000/api/v1/vault/projects/test-proj/secrets" \
     -H "Content-Type: application/json" \
     -H "X-Actor-Id: operator_1" \
     -d '{
       "scope_name": "common",
       "key": "DATABASE_URL",
       "value": "postgresql://user:secret123@db:5432/production"
     }'
```

### Expected Output in Terminal 1 (Within 1 Second):
```text
event: secret_update
data: {"event_id": "...", "project_id": "test-proj", "scope_name": "common", "changed_keys": ["DATABASE_URL"], "new_version": 1, "actor": "operator_1", "timestamp": "..."}
```

---

## Scenario 3: Validate Zero-Disk Artifact Invariant

Run the filesystem assertion script:
```bash
uv run python -c "
import os, glob
assert not os.path.exists('.env.runtime'), 'Plaintext runtime .env found!'
assert not os.path.exists('/tmp/dut_vault_secrets.json'), 'Plaintext tmp cache found!'
print('PASS: Zero disk artifacts confirmed.')
"
```

---

## Scenario 4: Validate In-Memory SDK Hot-Reload (< 5s)

### Step 4.1: Run the SDK Client Test Script
Execute a script simulating a long-running service:
```bash
uv run python -c "
import time
from packages.dut_vault_sdk import VaultClient

client = VaultClient(
    base_url='http://localhost:8000',
    project_id='test-proj',
    user_role='admin',
    scope='common',
)
client.connect()

print('Initial DATABASE_URL:', client.get('DATABASE_URL'))

# Wait for background stream mutation
print('Waiting for hot-reload event (max 5s)...')
start = time.time()
initial_val = client.get('DATABASE_URL')
while time.time() - start < 6.0:
    current_val = client.get('DATABASE_URL')
    if current_val != initial_val:
        elapsed = time.time() - start
        print(f'HOT-RELOAD SUCCESS in {elapsed:.2f}s! New value: {current_val}')
        break
    time.sleep(0.2)
else:
    print('TIMEOUT: Secret did not update within 5 seconds.')
"
```

### Step 4.2: Trigger Secret Update While Script is Waiting
```bash
curl -X POST "http://localhost:8000/api/v1/vault/projects/test-proj/secrets" \
     -H "Content-Type: application/json" \
     -d '{
       "scope_name": "common",
       "key": "DATABASE_URL",
       "value": "postgresql://user:rotated_pass@db:5432/production"
     }'
```

### Expected Output:
```text
Initial DATABASE_URL: postgresql://user:secret123@db:5432/production
Waiting for hot-reload event (max 5s)...
HOT-RELOAD SUCCESS in 0.45s! New value: postgresql://user:rotated_pass@db:5432/production
```
