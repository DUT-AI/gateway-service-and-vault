"use client";

import React, { useState } from "react";
import {
  Check,
  Container,
  Copy,
  FileCode,
  ShieldCheck,
  Terminal,
  FolderLock,
  Layers,
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

export interface DockerDeploymentGuideDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const DOCKER_COMPOSE_SNIPPET = `version: "3.8"

services:
  backend-worker:
    build: .
    restart: unless-stopped
    environment:
      # Địa chỉ Gateway mTLS cổng 9443
      - GATEWAY_URL=https://gateway:9443
      - X_PROJECT_ID=\${X_PROJECT_ID}
      - X_VIRTUAL_KEY=\${X_VIRTUAL_KEY}
      - SSL_CERT_FILE=/etc/ssl/certs/client.crt
      - SSL_KEY_FILE=/etc/ssl/private/client.key
    volumes:
      # Mount chứng chỉ mTLS vào container ở chế độ Read-Only (:ro)
      - ./certs/client.crt:/etc/ssl/certs/client.crt:ro
      - ./certs/client.key:/etc/ssl/private/client.key:ro
    extra_hosts:
      - "host.docker.internal:host-gateway"`;

const PYTHON_REQUEST_SNIPPET = `import httpx
import os

# Đường dẫn chứng chỉ mTLS đã được mount vào container
cert = (
    os.getenv("SSL_CERT_FILE", "/etc/ssl/certs/client.crt"),
    os.getenv("SSL_KEY_FILE", "/etc/ssl/private/client.key"),
)

headers = {
    "X-Virtual-Key": os.getenv("X_VIRTUAL_KEY"),
    "X-Project-Id": os.getenv("X_PROJECT_ID"),
}

async with httpx.AsyncClient(cert=cert, verify=False) as client:
    response = await client.get(
        "https://host.docker.internal:9443/services/llm/models",
        headers=headers,
    )
    print("Gateway Response:", response.json())`;

const CURL_TEST_SNIPPET = `docker compose exec backend-worker curl -k \\
  --cert /etc/ssl/certs/client.crt \\
  --key /etc/ssl/private/client.key \\
  -H "X-Virtual-Key: \${X_VIRTUAL_KEY}" \\
  -H "X-Project-Id: \${X_PROJECT_ID}" \\
  https://host.docker.internal:9443/services/llm/models`;

export function DockerDeploymentGuideDialog({
  open,
  onOpenChange,
}: DockerDeploymentGuideDialogProps) {
  const [activeTab, setActiveTab] = useState<"compose" | "python" | "curl">("compose");
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

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
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
              <Container className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold text-slate-900">
                Hướng dẫn triển khai Docker Workload (App Server)
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500">
                Cấu hình mount chứng chỉ mTLS và nạp Virtual Key vào Docker container an toàn.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        {/* 3 Step Workflow Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-2">
          <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-3 text-xs">
            <div className="flex items-center gap-1.5 font-semibold text-slate-800">
              <FolderLock className="h-4 w-4 text-blue-600" />
              <span>1. Chuẩn bị file</span>
            </div>
            <p className="mt-1 text-slate-500 text-[11px] leading-relaxed">
              Tạo thư mục <code className="font-mono bg-white px-1 rounded border">./certs/</code> và lưu <code className="font-mono">client.crt</code> & <code className="font-mono">client.key</code>.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-3 text-xs">
            <div className="flex items-center gap-1.5 font-semibold text-slate-800">
              <Layers className="h-4 w-4 text-purple-600" />
              <span>2. Mount Volume</span>
            </div>
            <p className="mt-1 text-slate-500 text-[11px] leading-relaxed">
              Mount chứng chỉ ở chế độ Read-Only (<code className="font-mono">:ro</code>) vào container.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-3 text-xs">
            <div className="flex items-center gap-1.5 font-semibold text-slate-800">
              <ShieldCheck className="h-4 w-4 text-emerald-600" />
              <span>3. Xác thực mTLS</span>
            </div>
            <p className="mt-1 text-slate-500 text-[11px] leading-relaxed">
              Gửi request qua port 9443 với header <code className="font-mono">X-Virtual-Key</code>.
            </p>
          </div>
        </div>

        {/* Tabs Switcher */}
        <div className="mt-2 flex items-center gap-1.5 border-b border-slate-200 text-xs">
          <button
            type="button"
            onClick={() => setActiveTab("compose")}
            className={`inline-flex items-center gap-1.5 border-b-2 px-3 py-2 font-medium transition-colors ${
              activeTab === "compose"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <FileCode className="h-3.5 w-3.5" />
            docker-compose.yml
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("python")}
            className={`inline-flex items-center gap-1.5 border-b-2 px-3 py-2 font-medium transition-colors ${
              activeTab === "python"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <Terminal className="h-3.5 w-3.5" />
            Python (httpx)
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("curl")}
            className={`inline-flex items-center gap-1.5 border-b-2 px-3 py-2 font-medium transition-colors ${
              activeTab === "curl"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <Terminal className="h-3.5 w-3.5" />
            Kiểm thử cURL
          </button>
        </div>

        {/* Tab Contents */}
        <div className="relative mt-2">
          {activeTab === "compose" && (
            <div>
              <div className="flex items-center justify-between pb-1.5 text-xs text-slate-500">
                <span>Cấu hình volume mounts và biến môi trường:</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopy(DOCKER_COMPOSE_SNIPPET, "compose")}
                  className="h-7 px-2 text-xs text-slate-600 hover:text-slate-900"
                >
                  {copiedKey === "compose" ? (
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
              <pre className="max-h-72 overflow-auto rounded-xl bg-slate-950 p-3.5 font-mono text-[11px] leading-relaxed text-blue-300">
                {DOCKER_COMPOSE_SNIPPET}
              </pre>
            </div>
          )}

          {activeTab === "python" && (
            <div>
              <div className="flex items-center justify-between pb-1.5 text-xs text-slate-500">
                <span>Mẫu gọi upstream API qua mTLS Client:</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopy(PYTHON_REQUEST_SNIPPET, "python")}
                  className="h-7 px-2 text-xs text-slate-600 hover:text-slate-900"
                >
                  {copiedKey === "python" ? (
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
              <pre className="max-h-72 overflow-auto rounded-xl bg-slate-950 p-3.5 font-mono text-[11px] leading-relaxed text-emerald-300">
                {PYTHON_REQUEST_SNIPPET}
              </pre>
            </div>
          )}

          {activeTab === "curl" && (
            <div>
              <div className="flex items-center justify-between pb-1.5 text-xs text-slate-500">
                <span>Lệnh kiểm tra kết nối từ container:</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopy(CURL_TEST_SNIPPET, "curl")}
                  className="h-7 px-2 text-xs text-slate-600 hover:text-slate-900"
                >
                  {copiedKey === "curl" ? (
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
              <pre className="max-h-72 overflow-auto rounded-xl bg-slate-950 p-3.5 font-mono text-[11px] leading-relaxed text-amber-300">
                {CURL_TEST_SNIPPET}
              </pre>
            </div>
          )}
        </div>

        {/* Security Footer Notice */}
        <div className="mt-3 rounded-lg bg-slate-100 p-3 text-[11px] text-slate-600 dark:bg-slate-800 dark:text-slate-400">
          <strong>Lưu ý bảo mật:</strong> Không bao giờ commit file <code className="font-mono text-rose-600">*.key</code> vào git repository. Hãy thêm dòng <code className="font-mono">certs/*.key</code> vào file <code className="font-mono">.gitignore</code>.
        </div>
      </DialogContent>
    </Dialog>
  );
}
