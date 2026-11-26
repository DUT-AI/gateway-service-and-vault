"use client";

import React, { useState } from "react";
import { Check, Copy, Globe, ShieldCheck, Terminal } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { ProjectAllowedService } from "../types";

export interface ServiceUsageDialogProps {
  projectId: string;
  service: ProjectAllowedService | null;
  onClose: () => void;
}

type UsageTab = "curl" | "python" | "openai";

const GATEWAY_BASE_URL = "https://gateway.dutai.io.vn";

export function ServiceUsageDialog({
  projectId,
  service,
  onClose,
}: ServiceUsageDialogProps) {
  const [activeTab, setActiveTab] = useState<UsageTab>("curl");
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  if (!service) return null;

  const gatewayEndpoint = `${GATEWAY_BASE_URL}/services/${service.service_slug}`;

  const snippets: Record<
    UsageTab,
    { label: string; subtitle: string; code: string }
  > = {
    curl: {
      label: "cURL",
      subtitle: "Gọi trực tiếp qua Gateway bằng chứng chỉ mTLS + X-Virtual-Key:",
      code: `curl --cert ~/.dut-vault/client.crt --key ~/.dut-vault/client.key \\
  -H "X-Virtual-Key: <VIRTUAL_KEY>" \\
  -H "X-Project-Id: ${projectId}" \\
  -H "Content-Type: application/json" \\
  ${gatewayEndpoint}/`,
    },
    python: {
      label: "Python (SDK)",
      subtitle:
        "Tự động nạp ~/.dut-vault/ và base_url mặc định (hoặc đặt env X_VIRTUAL_KEY thay cho virtual_key):",
      code: `from dut_vault_sdk import VaultClient

vault = VaultClient(
    project_id="${projectId}",
    virtual_key="<VIRTUAL_KEY>",  # hoặc đặt biến môi trường X_VIRTUAL_KEY
)

with vault.gateway_client("${service.service_slug}") as client:
    res = client.get("/")
    print(res.status_code, res.text)`,
    },
    openai: {
      label: "OpenAI / LLM SDK",
      subtitle:
        "Dành cho dịch vụ LLM tương thích OpenAI (không cần tự cấu hình cert):",
      code: `from openai import OpenAI
from dut_vault_sdk import VaultClient

vault = VaultClient(
    project_id="${projectId}",
    virtual_key="<VIRTUAL_KEY>",  # hoặc đặt biến môi trường X_VIRTUAL_KEY
)

client = OpenAI(
    base_url="${gatewayEndpoint}",
    api_key="managed-by-gateway",
    http_client=vault.gateway_client(),
)`,
    },
  };

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

  const active = snippets[activeTab];

  return (
    <Dialog open={Boolean(service)} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#EEF3FA] text-[#042B5F]">
              <Terminal className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold text-slate-900">
                Cách gọi dịch vụ: {service.service_name}
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500">
                Gọi qua Zero-Trust Gateway (không gọi trực tiếp upstream URL).
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        {/* Gateway Proxy URL */}
        <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-3.5 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-slate-700 flex items-center gap-1.5">
              <Globe className="h-3.5 w-3.5 text-[#042B5F]" />
              Gateway Base URL:
            </span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => handleCopy(gatewayEndpoint, "url")}
              className="h-6 px-2 text-xs text-slate-600 hover:text-slate-900"
            >
              {copiedKey === "url" ? (
                <>
                  <Check className="h-3 w-3 mr-1 text-emerald-600" />
                  Đã chép
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3 mr-1" />
                  Sao chép URL
                </>
              )}
            </Button>
          </div>

          <div className="font-mono text-xs bg-white border border-slate-200 rounded-lg px-3 py-2 text-[#042B5F] break-all select-all">
            {gatewayEndpoint}
          </div>

          <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-500">
            <span>
              Gateway tự chuyển tiếp tới{" "}
              <code className="font-mono text-slate-700">
                {service.base_url}
              </code>
            </span>
            <Badge variant="outline" className="text-[10px] bg-white font-mono">
              {service.auth_type}
            </Badge>
          </div>
        </div>

        {/* Code Examples */}
        <div className="space-y-2">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <span className="text-xs font-semibold text-slate-800">
              Code mẫu tích hợp:
            </span>
            <div className="flex items-center gap-1">
              {(Object.keys(snippets) as UsageTab[]).map((tab) => (
                <button
                  key={tab}
                  type="button"
                  onClick={() => setActiveTab(tab)}
                  className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-colors ${
                    activeTab === tab
                      ? "bg-[#042B5F] text-white"
                      : "text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  {snippets[tab].label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500">
            <span>{active.subtitle}</span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => handleCopy(active.code, activeTab)}
              className="h-6 px-2 text-xs text-slate-600 hover:text-slate-900 shrink-0"
            >
              {copiedKey === activeTab ? (
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
            {active.code}
          </pre>
        </div>

        <div className="flex items-center gap-2 rounded-lg bg-emerald-50 p-2.5 text-[11px] text-emerald-800 border border-emerald-200">
          <ShieldCheck className="h-4 w-4 shrink-0 text-emerald-600" />
          <span>
            Hạn mức áp dụng cho dự án:{" "}
            <strong>{service.rate_limit_rpm} RPM</strong> &middot;{" "}
            <strong>{service.quota_daily.toLocaleString("vi-VN")} req/ngày</strong>.
          </span>
        </div>
      </DialogContent>
    </Dialog>
  );
}
