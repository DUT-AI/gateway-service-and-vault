# dut-vault-sdk

Client SDK and CLI process runner for **DUT-AI Dynamic Vault & Zero-Trust Gateway**:
- **100% In-Memory RAM storage** (`os.environ`) — zero plaintext `.env` disk artifacts
- **Auto-discovery mTLS** (`~/.dut-vault/client.crt`, `~/.dut-vault/client.key`) & `X_VIRTUAL_KEY`
- **Real-Time SSE Hot-Reload** (< 5s latency)
- **Pre-configured Gateway HTTP client** (`vault.gateway_client("<service_slug>")`)

## Installation

```bash
# Using pip
pip install dut-vault-sdk

# Using uv
uv add dut-vault-sdk
```

## Quick Start

### 1. Load Vault Secrets in Python

```python
import os
from dut_vault_sdk import VaultClient

# Automatically loads ~/.dut-vault/client.crt, client.key & X_VIRTUAL_KEY from env
vault = VaultClient(
    base_url="https://gateway.dutai.io.vn",
    project_id="<PROJECT_ID>",
    scope="Common",
    inject_environ=True,
)

vault.connect(wait_for_stream=True)

openai_key = vault.get("OPENAI_API_KEY", default="")
db_url = os.getenv("DATABASE_URL")
```

### 2. Call Upstream Services via Zero-Trust Gateway

```python
from dut_vault_sdk import VaultClient

vault = VaultClient(base_url="https://gateway.dutai.io.vn")

with vault.gateway_client("llm") as client:
    res = client.post("/chat/completions", json={"model": "...", "messages": [...]})
```

### 3. CLI Process Runner (Any Language)

```bash
X_VIRTUAL_KEY=<VIRTUAL_KEY> dut-vault run \
  --project <PROJECT_ID> \
  --api-url https://gateway.dutai.io.vn \
  -- python main.py
```
