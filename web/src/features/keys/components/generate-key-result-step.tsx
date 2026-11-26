"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  Check,
  Copy,
  ShieldCheck,
  Terminal,
} from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { GenerateKeyResult } from "../types";

export interface GenerateKeyResultStepProps {
  result: GenerateKeyResult | null;
  onDone: () => void;
}

export function GenerateKeyResultStep({
  result,
  onDone,
}: GenerateKeyResultStepProps) {
  const [copiedKey, setCopiedKey] = useState(false);
  const [copiedCommand, setCopiedCommand] = useState(false);

  const cliCommand = result
    ? `dut-vault run --key=${result.virtual_key} -- python main.py`
    : "";

  const handleCopyKey = async () => {
    if (!result?.virtual_key) return;
    try {
      await navigator.clipboard.writeText(result.virtual_key);
      setCopiedKey(true);
      toast.success("Đã sao chép Virtual Key vào bộ nhớ tạm");
      setTimeout(() => setCopiedKey(false), 2000);
    } catch {
      toast.error("Không thể sao chép Virtual Key");
    }
  };

  const handleCopyCommand = async () => {
    if (!cliCommand) return;
    try {
      await navigator.clipboard.writeText(cliCommand);
      setCopiedCommand(true);
      toast.success("Đã sao chép lệnh thực thi CLI");
      setTimeout(() => setCopiedCommand(false), 2000);
    } catch {
      toast.error("Không thể sao chép lệnh CLI");
    }
  };

  return (
    <>
      <DialogHeader>
        <div className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <DialogTitle className="text-base font-semibold text-slate-900">
              Virtual Key đã được tạo thành công
            </DialogTitle>
            <DialogDescription className="text-xs text-slate-500">
              Khóa ảo truy cập Gateway đã sẵn sàng để tích hợp vào ứng dụng.
            </DialogDescription>
          </div>
        </div>
      </DialogHeader>

      <div className="space-y-4 pt-1">
        <div className="rounded-xl border border-amber-200 bg-amber-50/80 p-3.5 space-y-1.5 text-xs text-amber-950">
          <div className="flex items-center gap-2 font-semibold">
            <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" />
            <span>Chỉ hiển thị 1 lần duy nhất</span>
          </div>
          <p className="text-[11px] text-amber-800 leading-relaxed">
            Vì lý do an toàn, mã bí mật Virtual Key đầy đủ sẽ không thể được
            xem lại sau khi đóng cửa sổ này. Hãy sao chép và lưu vào biến môi
            trường hoặc file cấu hình an toàn của dự án.
          </p>
        </div>

        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-700">
              Mã khóa truy cập (Virtual Access Key):
            </span>
            <Badge variant="outline" className="text-[10px] bg-slate-50 font-mono">
              Prefix: {result?.key_prefix}
            </Badge>
          </div>

          <div className="flex items-center gap-2 bg-slate-900 text-emerald-400 p-3 rounded-xl font-mono text-xs border border-slate-800">
            <span className="break-all flex-1 select-all font-mono">
              {result?.virtual_key}
            </span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleCopyKey}
              className="h-7 px-2 text-slate-300 hover:text-white hover:bg-slate-800 shrink-0"
              title="Sao chép Virtual Key"
            >
              {copiedKey ? (
                <Check className="h-3.5 w-3.5 text-emerald-400" />
              ) : (
                <Copy className="h-3.5 w-3.5" />
              )}
            </Button>
          </div>
        </div>

        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-700 flex items-center gap-1.5">
              <Terminal className="h-3.5 w-3.5 text-[#042B5F]" />
              Lệnh thực thi mẫu với CLI SDK:
            </span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleCopyCommand}
              className="h-6 px-2 text-xs text-[#042B5F] hover:text-[#031F46] hover:bg-[#EEF3FA]"
            >
              {copiedCommand ? (
                <>
                  <Check className="h-3 w-3 mr-1 text-emerald-600" />
                  Đã chép
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3 mr-1 text-[#042B5F]" />
                  Sao chép lệnh
                </>
              )}
            </Button>
          </div>

          <div className="bg-slate-950 text-slate-200 p-3 rounded-xl font-mono text-[11px] border border-slate-800 overflow-x-auto select-all">
            <code>{cliCommand}</code>
          </div>
          <p className="text-[10px] text-slate-400">
            Lệnh trên tự động nạp cấu hình và xác thực mTLS từ chứng chỉ đã cài
            đặt trên máy.
          </p>
        </div>
      </div>

      <DialogFooter className="pt-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onDone}
          className="w-full sm:w-auto text-xs"
        >
          Đã lưu an toàn & Hoàn tất
        </Button>
      </DialogFooter>
    </>
  );
}
