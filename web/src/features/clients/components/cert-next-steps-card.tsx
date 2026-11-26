"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  Check,
  Container,
  Copy,
  KeyRound,
  Send,
  Terminal,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import type { RegisterClientResult } from "../types";

export interface CertNextStepsCardProps {
  bundle: RegisterClientResult;
  isOtherRole: boolean;
  onNavigateToProjects: () => void;
  onOpenDockerGuide?: () => void;
}

const VERIFY_SNIPPET = `curl --cert ~/.dut-vault/client.crt --key ~/.dut-vault/client.key \\
  -H "X-Virtual-Key: <VIRTUAL_KEY>" \\
  https://gateway.dutai.io.vn/api/v1/health`;

export function CertNextStepsCard({
  bundle,
  isOtherRole,
  onNavigateToProjects,
  onOpenDockerGuide,
}: CertNextStepsCardProps) {
  const [copiedHandoff, setCopiedHandoff] = useState(false);
  const [copiedVerify, setCopiedVerify] = useState(false);

  const handoffMessage = `Mình đã đăng ký thiết bị mTLS "${bundle.name}" (Fingerprint: ${bundle.cert_fingerprint}). Nhờ Project Developer cấp giúp Virtual Key cho thiết bị này trong dự án nhé!`;

  const handleCopyHandoff = async () => {
    try {
      await navigator.clipboard.writeText(handoffMessage);
      setCopiedHandoff(true);
      toast.success("Đã sao chép thông tin gửi Project Developer");
      setTimeout(() => setCopiedHandoff(false), 2000);
    } catch {
      toast.error("Không thể sao chép nội dung");
    }
  };

  const handleCopyVerify = async () => {
    try {
      await navigator.clipboard.writeText(VERIFY_SNIPPET);
      setCopiedVerify(true);
      toast.success("Đã sao chép lệnh kiểm tra kết nối");
      setTimeout(() => setCopiedVerify(false), 2000);
    } catch {
      toast.error("Không thể sao chép lệnh");
    }
  };

  return (
    <div className="rounded-xl border border-[#042B5F]/15 bg-[#EEF3FA] p-3.5 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[#042B5F] text-[11px] font-bold text-white">
              3
            </span>
            <span className="text-xs font-semibold text-[#042B5F]">
              {isOtherRole
                ? "Nhận Virtual Key từ Project Developer"
                : "Cấp Virtual Key cho thiết bị trong Dự án"}
            </span>
          </div>
          <p className="text-[11px] text-slate-600 leading-relaxed pl-7">
            {isOtherRole ? (
              <>
                Thiết bị của bạn đã sẵn sàng. Hãy báo cho{" "}
                <strong className="text-slate-800">Project Developer</strong>{" "}
                gán Virtual Key cho thiết bị này trong tab{" "}
                <strong className="text-slate-800">Virtual Keys</strong> của dự
                án; sau đó bạn có thể xem key tại đó.
              </>
            ) : (
              <>
                Vào trang chi tiết <strong className="text-slate-800">Dự án</strong>{" "}
                → tab <strong className="text-slate-800">Virtual Keys</strong>{" "}
                → chọn thiết bị <strong className="text-slate-800">{bundle.name}</strong>{" "}
                để phát hành API Key.
              </>
            )}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 pl-7">
        {isOtherRole && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleCopyHandoff}
            className="h-8 text-xs bg-white border-[#042B5F]/20 text-[#042B5F] hover:bg-[#E1EAF6]"
          >
            {copiedHandoff ? (
              <>
                <Check className="h-3.5 w-3.5 mr-1.5 text-emerald-600" />
                Đã sao chép tin nhắn
              </>
            ) : (
              <>
                <Send className="h-3.5 w-3.5 mr-1.5" />
                Sao chép thông tin gửi Project Developer
              </>
            )}
          </Button>
        )}

        <Button
          type="button"
          variant={isOtherRole ? "ghost" : "outline"}
          size="sm"
          asChild
          className="h-8 text-xs border-[#042B5F]/20 bg-white text-[#042B5F] hover:bg-[#E1EAF6]"
        >
          <Link href="/projects" onClick={onNavigateToProjects}>
            <KeyRound className="h-3.5 w-3.5 mr-1.5" />
            Tới Dự án
            <ArrowRight className="h-3 w-3 ml-1" />
          </Link>
        </Button>

        {!isOtherRole &&
          bundle.client_type === "APP_SERVER" &&
          onOpenDockerGuide && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={onOpenDockerGuide}
              className="h-8 text-xs bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
            >
              <Container className="h-3.5 w-3.5 mr-1.5 text-[#042B5F]" />
              Hướng dẫn Docker Workload
            </Button>
          )}
      </div>

      {/* Quick Verification Snippet */}
      <div className="pl-7 pt-1">
        <div className="flex items-center justify-between text-[11px] text-slate-600 mb-1">
          <span className="inline-flex items-center gap-1 font-medium">
            <Terminal className="h-3 w-3 text-slate-500" />
            Kiểm tra nhanh sau khi có Virtual Key:
          </span>
          <button
            type="button"
            onClick={handleCopyVerify}
            className="inline-flex items-center gap-1 text-[#042B5F] hover:text-[#031F46] font-medium"
          >
            {copiedVerify ? (
              <>
                <Check className="h-3 w-3 text-emerald-600" />
                Đã chép
              </>
            ) : (
              <>
                <Copy className="h-3 w-3" />
                Sao chép
              </>
            )}
          </button>
        </div>
        <pre className="rounded-lg bg-slate-900 text-slate-200 px-3 py-2 font-mono text-[10px] overflow-x-auto">
          {VERIFY_SNIPPET}
        </pre>
      </div>
    </div>
  );
}
