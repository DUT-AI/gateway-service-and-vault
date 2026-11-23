"use client";

import React, { useState } from "react";
import {
  Check,
  Code2,
  Copy,
  Cpu,
  Flame,
  Radio,
  ShieldCheck,
  Terminal,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export interface SdkQuickstartDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: string;
  projectName: string;
  selectedScope?: string;
}

export function SdkQuickstartDialog({
  open,
  onOpenChange,
  projectId,
  projectName,
  selectedScope = "production",
}: SdkQuickstartDialogProps) {
  const [activeTab, setActiveTab] = useState<"async" | "sync" | "cli">("async");
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const scopeName = selectedScope === "ALL" ? "production" : selectedScope;

  const PIP_INSTALL_CMD = "pip install dut-vault-sdk";

  const ASYNC_PYTHON_SNIPPET = `import os
from dut_vault_sdk import DutVaultClient

async def setup_vault():
    # Khởi tạo client kết nối Dynamic Vault qua mTLS + Virtual Key
    vault = DutVaultClient(
        base_url="https://gateway.dutai.io.vn",
        project_id="${projectId}",  # ${projectName}
        scope="${scopeName}",
        client_cert=os.getenv("SSL_CERT_FILE", "./certs/client.crt"),
        client_key=os.getenv("SSL_KEY_FILE", "./certs/client.key"),
        virtual_key=os.getenv("X_VIRTUAL_KEY"),
    )

    # 1. Nạp trực tiếp toàn bộ biến bí mật vào RAM (os.environ) - Zero .env files!
    await vault.load_into_environ()
    print("✅ Đã nạp biến môi trường thành công vào RAM!")

    # 2. Đăng ký callback Hot-Reload tự động khi Secret thay đổi trên Vault (< 5s)
    @vault.on_reload
    async def handle_secrets_rotation(updated_keys: list[str]):
        print(f"🔄 Nhận cập nhật thời gian thực từ Vault SSE: {updated_keys}")
        # Tự động reload connection pool hoặc LLM client tại đây

    # Bắt đầu lắng nghe SSE background stream
    await vault.start_hot_reload_listener()`;

  const SYNC_PYTHON_SNIPPET = `import os
from dut_vault_sdk import DutVaultSyncClient

# Khởi tạo đồng bộ trước khi start ứng dụng (FastAPI, Django, Celery)
vault = DutVaultSyncClient(
    base_url="https://gateway.dutai.io.vn",
    project_id="${projectId}",  # ${projectName}
    scope="${scopeName}",
    client_cert=os.getenv("SSL_CERT_FILE", "./certs/client.crt"),
    client_key=os.getenv("SSL_KEY_FILE", "./certs/client.key"),
    virtual_key=os.getenv("X_VIRTUAL_KEY"),
)

# Nạp vào os.environ trước khi nạp app config
vault.load_into_environ()
print("✅ Secrets loaded into memory without writing .env to disk.")`;

  const handleCopy = async (text: string, key: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedKey(key);
      toast.success("Đã sao chép vào bộ nhớ tạm");
      setTimeout(() => setCopiedKey(null), 2000);
    } catch {
      toast.error("Không thể sao chép");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-purple-100 text-purple-700">
              <Terminal className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold text-slate-900">
                Tích hợp SDK Vault (Zero .env In-Memory Hot-Reload)
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500">
                Dự án: <strong className="text-slate-800">{projectName}</strong> (ID: {projectId})
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        {/* Core Principles Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-2">
          <div className="rounded-xl border border-blue-200 bg-blue-50/50 p-3 text-xs">
            <div className="flex items-center gap-1.5 font-semibold text-blue-900">
              <Cpu className="h-4 w-4 text-blue-600" />
              <span>Nguyên tắc Zero .env</span>
            </div>
            <p className="mt-1 text-slate-600 text-[11px] leading-relaxed">
              Tuyệt đối không lưu file <code className="font-mono bg-white px-1 rounded border">.env</code> plaintext trên đĩa. SDK nạp thẳng dữ liệu vào RAM tiến trình (<code className="font-mono">os.environ</code>).
            </p>
          </div>

          <div className="rounded-xl border border-purple-200 bg-purple-50/50 p-3 text-xs">
            <div className="flex items-center gap-1.5 font-semibold text-purple-900">
              <Flame className="h-4 w-4 text-purple-600" />
              <span>Real-Time Hot-Reload</span>
            </div>
            <p className="mt-1 text-slate-600 text-[11px] leading-relaxed">
              Khi Secret được cập nhật hoặc thu hồi, tiến trình nhận sự kiện qua SSE Stream và tự động cập nhật trong &lt; 5 giây không cần restart server.
            </p>
          </div>
        </div>

        {/* Step 1: Install SDK */}
        <div className="space-y-1.5 pt-1">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-800">
            <span>Bước 1: Cài đặt gói thư viện Python SDK</span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => handleCopy(PIP_INSTALL_CMD, "pip")}
              className="h-6 px-2 text-xs text-slate-600 hover:text-slate-900"
            >
              {copiedKey === "pip" ? (
                <>
                  <Check className="h-3 w-3 mr-1 text-emerald-600" />
                  Đã chép
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3 mr-1" />
                  Sao chép
                </>
              )}
            </Button>
          </div>
          <div className="flex items-center justify-between rounded-xl bg-slate-950 px-3.5 py-2.5 font-mono text-xs text-emerald-400">
            <code>{PIP_INSTALL_CMD}</code>
          </div>
        </div>

        {/* Step 2: Code Snippets */}
        <div className="space-y-1.5 pt-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-800">
              Bước 2: Đoạn mã tích hợp vào ứng dụng
            </span>

            {/* Language tabs */}
            <div className="flex items-center gap-1 text-xs">
              <button
                type="button"
                onClick={() => setActiveTab("async")}
                className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-colors ${
                  activeTab === "async"
                    ? "bg-blue-600 text-white"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                Async (FastAPI / Sanic)
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("sync")}
                className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-colors ${
                  activeTab === "sync"
                    ? "bg-blue-600 text-white"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                Sync (Django / Flask)
              </button>
            </div>
          </div>

          <div className="relative">
            {activeTab === "async" && (
              <div>
                <div className="flex items-center justify-between pb-1 text-xs text-slate-500">
                  <span className="inline-flex items-center gap-1">
                    <Radio className="h-3 w-3 text-emerald-500 animate-pulse" />
                    Kèm bộ lắng nghe SSE Hot-Reload tức thời:
                  </span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopy(ASYNC_PYTHON_SNIPPET, "async_code")}
                    className="h-6 px-2 text-xs text-slate-600 hover:text-slate-900"
                  >
                    {copiedKey === "async_code" ? (
                      <>
                        <Check className="h-3 w-3 mr-1 text-emerald-600" />
                        Đã chép
                      </>
                    ) : (
                      <>
                        <Copy className="h-3 w-3 mr-1" />
                        Sao chép code
                      </>
                    )}
                  </Button>
                </div>
                <pre className="max-h-72 overflow-auto rounded-xl bg-slate-950 p-3.5 font-mono text-[11px] leading-relaxed text-blue-300">
                  {ASYNC_PYTHON_SNIPPET}
                </pre>
              </div>
            )}

            {activeTab === "sync" && (
              <div>
                <div className="flex items-center justify-between pb-1 text-xs text-slate-500">
                  <span>Nạp cấu hình đồng bộ khi ứng dụng khởi chạy:</span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopy(SYNC_PYTHON_SNIPPET, "sync_code")}
                    className="h-6 px-2 text-xs text-slate-600 hover:text-slate-900"
                  >
                    {copiedKey === "sync_code" ? (
                      <>
                        <Check className="h-3 w-3 mr-1 text-emerald-600" />
                        Đã chép
                      </>
                    ) : (
                      <>
                        <Copy className="h-3 w-3 mr-1" />
                        Sao chép code
                      </>
                    )}
                  </Button>
                </div>
                <pre className="max-h-72 overflow-auto rounded-xl bg-slate-950 p-3.5 font-mono text-[11px] leading-relaxed text-emerald-300">
                  {SYNC_PYTHON_SNIPPET}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Security badge footer */}
        <div className="mt-2 flex items-center gap-2 rounded-lg bg-emerald-50 p-2.5 text-[11px] text-emerald-800 border border-emerald-200">
          <ShieldCheck className="h-4 w-4 shrink-0 text-emerald-600" />
          <span>
            Bảo mật tối đa: Dữ liệu được mã hóa <strong>AES-256-GCM</strong> và phân quyền chi tiết theo từng khóa (Key-Level Permissions) cho từng danh tính lập trình viên.
          </span>
        </div>
      </DialogContent>
    </Dialog>
  );
}
