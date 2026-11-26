export interface SdkQuickstartSnippets {
  pipInstall: string;
  cli: string;
  asyncPython: string;
  syncPython: string;
  curl: string;
}

export function buildSdkQuickstartSnippets(
  projectId: string,
  projectName: string,
  scopeName: string
): SdkQuickstartSnippets {
  const scopeFlag = scopeName && scopeName !== "ALL" ? ` --scope ${scopeName}` : "";
  const scopeArg =
    scopeName && scopeName !== "ALL" ? `"${scopeName}"` : "None";

  return {
    pipInstall: "pip install dut-vault-sdk  # hoặc: uv add dut-vault-sdk",
    cli: `# Tự động dùng chứng chỉ tại ~/.dut-vault/, base_url mặc định https://gateway.dutai.io.vn
X_VIRTUAL_KEY=<VIRTUAL_KEY> dut-vault run \\
  --project ${projectId}${scopeFlag} \\
  -- python main.py`,
    asyncPython: `from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from dut_vault_sdk import VaultClient

# Tự động nạp ~/.dut-vault/client.crt, client.key và base_url mặc định
vault = VaultClient(
    project_id="${projectId}",  # ${projectName}
    virtual_key="<VIRTUAL_KEY>",  # hoặc đặt biến môi trường X_VIRTUAL_KEY
    scope=${scopeArg},
    inject_environ=True,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await vault.connect_async(wait_for_stream=True)
    try:
        yield
    finally:
        await vault.disconnect_async()

app = FastAPI(lifespan=lifespan)

# Đọc biến mới nhất từ Vault (hoặc os.getenv("OPENAI_API_KEY")):
# openai_key = vault.get("OPENAI_API_KEY", default="")`,
    syncPython: `import os
from dut_vault_sdk import VaultClient

# Tự động nạp ~/.dut-vault/client.crt, client.key và base_url mặc định
vault = VaultClient(
    project_id="${projectId}",  # ${projectName}
    virtual_key="<VIRTUAL_KEY>",  # hoặc đặt biến môi trường X_VIRTUAL_KEY
    scope=${scopeArg},
    inject_environ=True,
)

# Nạp biến vào os.environ (RAM) & bật SSE hot-reload (< 5s)
vault.connect(wait_for_stream=True)

# Đọc biến từ Vault (luôn lấy giá trị mới nhất) hoặc qua os.getenv(...)
openai_key = vault.get("OPENAI_API_KEY", default="")
db_url = os.getenv("DATABASE_URL")`,
    curl: `curl --cert ~/.dut-vault/client.crt --key ~/.dut-vault/client.key \\
  -H "X-Virtual-Key: <VIRTUAL_KEY>" \\
  "https://gateway.dutai.io.vn/api/v1/vault/projects/${projectId}/secrets"`,
  };
}
