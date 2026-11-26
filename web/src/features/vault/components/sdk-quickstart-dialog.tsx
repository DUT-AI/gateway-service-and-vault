"use client";

import React, { useMemo, useState } from "react";
import {
  Check,
  Copy,
  Cpu,
  Flame,
  Globe,
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
import { buildSdkQuickstartSnippets } from "../utils/sdk-quickstart-snippets";

export interface SdkQuickstartDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: string;
  projectName: string;
  selectedScope?: string;
}

type GuideTab = "cli" | "async" | "sync" | "curl";

export function SdkQuickstartDialog({
  open,
  onOpenChange,
  projectId,
  projectName,
  selectedScope = "ALL",
}: SdkQuickstartDialogProps) {
  const [activeTab, setActiveTab] = useState<GuideTab>("cli");
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const snippets = useMemo(
    () => buildSdkQuickstartSnippets(projectId, projectName, selectedScope),
    [projectId, projectName, selectedScope]
  );

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

  const tabContent: Record<
    GuideTab,
    { label: string; subtitle: string; code: string; colorClass: string }
  > = {
    cli: {
      label: "CLI Runner",
      subtitle:
        "Chạy bất kỳ ứng dụng nào (Python, Node.js, Go...) với biến môi trường nạp thẳng vào RAM:",
      code: snippets.cli,
      colorClass: "text-emerald-300",
    },
    async: {
      label: "Async (FastAPI)",
      subtitle:
        "Tích hợp vào FastAPI lifespan kèm bộ lắng nghe SSE Hot-Reload tức thời:",
      code: snippets.asyncPython,
      colorClass: "text-blue-300",
    },
    sync: {
      label: "Sync (Python)",
      subtitle:
        "Nạp cấu hình đồng bộ vào os.environ khi khởi chạy Django, Flask hoặc script:",
      code: snippets.syncPython,
      colorClass: "text-emerald-300",
    },
    curl: {
      label: "HTTP / cURL",
      subtitle:
        "Gọi trực tiếp REST API qua mTLS + Virtual Key cho ngôn ngữ khác hoặc Docker:",
      code: snippets.curl,
      colorClass: "text-amber-300",
    },
  };

  const active = tabContent[activeTab];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#EEF3FA] text-[#042B5F]">
              <Terminal className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold text-slate-900">
                Hướng dẫn sử dụng biến môi trường (CLI & SDK)
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500">
                Dự án:{" "}
                <strong className="text-slate-800">{projectName}</strong> (ID:{" "}
                <span className="font-mono">{projectId}</span>)
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        {/* Core Principles Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
          <div className="rounded-xl border border-[#042B5F]/20 bg-[#EEF3FA] p-3 text-xs">
            <div className="flex items-center gap-1.5 font-semibold text-[#042B5F]">
              <Cpu className="h-4 w-4 text-[#042B5F]" />
              <span>Nguyên tắc Zero .env</span>
            </div>
            <p className="mt-1 text-slate-600 text-[11px] leading-relaxed">
              Không lưu file{" "}
              <code className="font-mono bg-white px-1 rounded border">
                .env
              </code>{" "}
              trên đĩa. SDK nạp thẳng vào RAM (
              <code className="font-mono">os.environ</code>) qua mTLS + Virtual
              Key.
            </p>
          </div>

          <div className="rounded-xl border border-purple-200 bg-purple-50/50 p-3 text-xs">
            <div className="flex items-center gap-1.5 font-semibold text-purple-900">
              <Flame className="h-4 w-4 text-purple-600" />
              <span>Real-Time Hot-Reload</span>
            </div>
            <p className="mt-1 text-slate-600 text-[11px] leading-relaxed">
              Khi Secret thay đổi trên Vault, tiến trình nhận sự kiện qua SSE
              Stream và tự động cập nhật trong &lt; 5 giây không cần restart.
            </p>
          </div>
        </div>

        {/* Step 1: Install SDK */}
        <div className="space-y-1.5 pt-1">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-800">
            <span>Bước 1: Cài đặt thư viện dut-vault-sdk</span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => handleCopy(snippets.pipInstall, "pip")}
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
          <div className="rounded-xl bg-slate-950 px-3.5 py-2.5 font-mono text-xs text-emerald-400">
            <code>{snippets.pipInstall}</code>
          </div>
        </div>

        {/* Step 2: Integration Tabs */}
        <div className="space-y-2 pt-1">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <span className="text-xs font-semibold text-slate-800">
              Bước 2: Chọn cách nạp biến vào dự án
            </span>

            <div className="flex items-center flex-wrap gap-1 text-xs">
              {(Object.keys(tabContent) as GuideTab[]).map((key) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setActiveTab(key)}
                  className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-colors inline-flex items-center gap-1 ${
                    activeTab === key
                      ? "bg-[#042B5F] text-white"
                      : "text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  {key === "curl" && <Globe className="h-3 w-3" />}
                  {tabContent[key].label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between pb-1 text-xs text-slate-500">
              <span className="inline-flex items-center gap-1 text-[11px]">
                {activeTab === "async" && (
                  <Radio className="h-3 w-3 text-emerald-500 animate-pulse" />
                )}
                {active.subtitle}
              </span>
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
                    Sao chép
                  </>
                )}
              </Button>
            </div>
            <pre
              className={`max-h-72 overflow-auto rounded-xl bg-slate-950 p-3.5 font-mono text-[11px] leading-relaxed ${active.colorClass}`}
            >
              {active.code}
            </pre>
          </div>
        </div>

        {/* Security badge footer */}
        <div className="mt-1 flex items-center gap-2 rounded-lg bg-emerald-50 p-2.5 text-[11px] text-emerald-800 border border-emerald-200">
          <ShieldCheck className="h-4 w-4 shrink-0 text-emerald-600" />
          <span>
            Yêu cầu thiết bị đã cài chứng chỉ tại{" "}
            <code className="font-mono bg-white px-1 rounded">
              ~/.dut-vault/
            </code>{" "}
            và có <strong>Virtual Key</strong> hợp lệ trong tab{" "}
            <strong>Virtual Keys</strong>.
          </span>
        </div>
      </DialogContent>
    </Dialog>
  );
}
