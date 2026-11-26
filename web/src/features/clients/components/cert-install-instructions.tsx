"use client";

import React, { useState } from "react";
import { Check, Container, Copy, Laptop, Terminal } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
type InstallTarget = "unix" | "windows" | "docker";

export interface CertInstallInstructionsProps {
  crtFilename: string;
  keyFilename: string;
  clientType: string;
}

export function CertInstallInstructions({
  crtFilename,
  keyFilename,
  clientType,
}: CertInstallInstructionsProps) {
  const [activeTab, setActiveTab] = useState<InstallTarget>(
    clientType === "APP_SERVER" ? "docker" : "unix"
  );
  const [copied, setCopied] = useState(false);

  const commands: Record<InstallTarget, string> = {
    unix: `mkdir -p ~/.dut-vault && \\
mv ~/Downloads/${crtFilename} ~/.dut-vault/client.crt && \\
mv ~/Downloads/${keyFilename} ~/.dut-vault/client.key && \\
chmod 600 ~/.dut-vault/client.key`,
    windows: `New-Item -ItemType Directory -Force -Path "$HOME\\.dut-vault" | Out-Null
Move-Item "$HOME\\Downloads\\${crtFilename}" "$HOME\\.dut-vault\\client.crt" -Force
Move-Item "$HOME\\Downloads\\${keyFilename}" "$HOME\\.dut-vault\\client.key" -Force`,
    docker: `mkdir -p ./certs && \\
mv ~/Downloads/${crtFilename} ./certs/client.crt && \\
mv ~/Downloads/${keyFilename} ./certs/client.key && \\
chmod 600 ./certs/client.key`,
  };

  const currentCommand = commands[activeTab];

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(currentCommand);
      setCopied(true);
      toast.success("Đã sao chép lệnh cài đặt chứng chỉ");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Không thể sao chép lệnh");
    }
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3.5 space-y-2.5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[#EEF3FA] text-[11px] font-bold text-[#042B5F]">
            2
          </span>
          <span className="text-xs font-semibold text-slate-800">
            Đưa tệp vào thư mục cấu hình & phân quyền
          </span>
        </div>

        <div className="inline-flex items-center rounded-lg bg-slate-100 p-0.5 border border-slate-200 text-[11px]">
          <button
            type="button"
            onClick={() => setActiveTab("unix")}
            className={`px-2 py-1 rounded-md font-medium transition-all flex items-center gap-1 ${
              activeTab === "unix"
                ? "bg-white text-slate-900 shadow-2xs"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            <Terminal className="h-3 w-3" />
            macOS / Linux
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("windows")}
            className={`px-2 py-1 rounded-md font-medium transition-all flex items-center gap-1 ${
              activeTab === "windows"
                ? "bg-white text-slate-900 shadow-2xs"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            <Laptop className="h-3 w-3" />
            Windows
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("docker")}
            className={`px-2 py-1 rounded-md font-medium transition-all flex items-center gap-1 ${
              activeTab === "docker"
                ? "bg-white text-slate-900 shadow-2xs"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            <Container className="h-3 w-3" />
            Docker
          </button>
        </div>
      </div>

      <div className="relative rounded-lg bg-slate-950 text-slate-100 p-3 pr-16 font-mono text-[11px] leading-relaxed overflow-x-auto border border-slate-800">
        <pre className="whitespace-pre-wrap break-all">{currentCommand}</pre>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={handleCopy}
          className="absolute top-2 right-2 h-7 px-2 text-[11px] text-slate-300 hover:text-white hover:bg-slate-800"
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 mr-1 text-emerald-400" />
              Đã chép
            </>
          ) : (
            <>
              <Copy className="h-3 w-3 mr-1" />
              Chép
            </>
          )}
        </Button>
      </div>

      <p className="text-[11px] text-slate-500 leading-relaxed">
        {activeTab === "docker"
          ? "Mount thư mục ./certs/client.crt và ./certs/client.key vào container ở chế độ :ro."
          : "Mặc định dut-vault-sdk và CLI sẽ tự động tìm chứng chỉ tại ~/.dut-vault/client.crt và ~/.dut-vault/client.key."}
      </p>
    </div>
  );
}
