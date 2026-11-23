"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  Check,
  Copy,
  ExternalLink,
  Key,
  KeyRound,
  Laptop,
  Loader2,
  Plus,
  Server,
  ShieldCheck,
  Terminal,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useClientsQuery } from "@/features/clients";
import { useGenerateKeyMutation } from "../hooks/use-keys-queries";
import type { GenerateKeyResult } from "../types";

export interface GenerateKeyModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: string;
}

export function GenerateKeyModal({
  open,
  onOpenChange,
  projectId,
}: GenerateKeyModalProps) {
  const { data: clients, isLoading: clientsLoading } = useClientsQuery();
  const generateMutation = useGenerateKeyMutation(projectId);

  const [selectedClientId, setSelectedClientId] = useState<string>("");
  const [step, setStep] = useState<"FORM" | "RESULT">("FORM");
  const [result, setResult] = useState<GenerateKeyResult | null>(null);

  const [copiedKey, setCopiedKey] = useState(false);
  const [copiedCommand, setCopiedCommand] = useState(false);

  // Filter only active, non-revoked, and unexpired client devices
  const activeClients = (clients ?? []).filter((client) => {
    if (client.is_revoked) return false;
    const isExpired = new Date(client.expires_at).getTime() < Date.now();
    return !isExpired;
  });

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      setStep("FORM");
      setResult(null);
      setSelectedClientId("");
      setCopiedKey(false);
      setCopiedCommand(false);
    }
    onOpenChange(nextOpen);
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedClientId) {
      toast.error("Vui lòng chọn thiết bị client được ràng buộc");
      return;
    }

    try {
      const data = await generateMutation.mutateAsync({
        client_id: selectedClientId,
        project_id: projectId,
      });

      setResult(data);
      setStep("RESULT");
      toast.success("Cấp Virtual Access Key thành công!");
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Đã xảy ra lỗi khi tạo Virtual Key";
      toast.error(msg);
    }
  };

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

  const cliCommand = result
    ? `dut-vault run --key=${result.virtual_key} -- python main.py`
    : "";

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
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-lg">
        {step === "FORM" ? (
          <>
            <DialogHeader>
              <div className="flex items-center gap-2.5">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
                  <KeyRound className="h-5 w-5" />
                </div>
                <div>
                  <DialogTitle className="text-base font-semibold text-slate-900">
                    Cấp Virtual Access Key mới
                  </DialogTitle>
                  <DialogDescription className="text-xs text-slate-500">
                    Tạo khóa ảo ràng buộc 1:1 với chứng chỉ mTLS phần cứng của thiết bị.
                  </DialogDescription>
                </div>
              </div>
            </DialogHeader>

            <form onSubmit={handleGenerate} className="space-y-4 pt-1">
              {/* Zero-Trust Client Binding Selector */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label
                    htmlFor="client-device"
                    className="text-xs font-semibold text-slate-700"
                  >
                    Thiết bị Client ràng buộc <span className="text-rose-500">*</span>
                  </Label>
                  <Link
                    href="/clients"
                    className="inline-flex items-center text-[11px] text-blue-600 hover:text-blue-700 font-medium"
                    target="_blank"
                  >
                    Quản lý thiết bị
                    <ExternalLink className="h-3 w-3 ml-0.5" />
                  </Link>
                </div>

                {clientsLoading ? (
                  <div className="h-9 w-full bg-slate-100 animate-pulse rounded-lg" />
                ) : activeClients.length === 0 ? (
                  <div className="rounded-xl border border-amber-200 bg-amber-50 p-3.5 space-y-2 text-xs text-amber-900">
                    <p className="font-semibold flex items-center gap-1.5">
                      <AlertTriangle className="h-4 w-4 text-amber-600" />
                      Chưa có thiết bị mTLS hợp lệ
                    </p>
                    <p className="text-[11px] text-amber-800 leading-relaxed">
                      Bạn cần đăng ký ít nhất một thiết bị mTLS đang hoạt động trước
                      khi có thể cấp phát Virtual Key.
                    </p>
                    <Link href="/clients">
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        className="h-7 text-xs bg-white border-amber-300 text-amber-900 hover:bg-amber-100 mt-1"
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        Đăng ký thiết bị ngay
                      </Button>
                    </Link>
                  </div>
                ) : (
                  <select
                    id="client-device"
                    value={selectedClientId}
                    onChange={(e) => setSelectedClientId(e.target.value)}
                    className="w-full h-9 rounded-lg border border-slate-200 bg-white px-3 text-xs text-slate-800 outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                  >
                    <option value="">-- Chọn thiết bị mTLS của bạn --</option>
                    {activeClients.map((client) => {
                      const isDev = client.client_type === "USER_DEVICE";
                      const fpSnippet = client.cert_fingerprint.slice(0, 14);
                      return (
                        <option key={client.id} value={client.id}>
                          {isDev ? "💻" : "🖥️"} {client.name} (
                          {isDev ? "Dev PC" : "Workload Server"} - FP: {fpSnippet}
                          ...)
                        </option>
                      );
                    })}
                  </select>
                )}

                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Nguyên tắc Zero-Trust Gatekeeper (Principle VIII): Khóa Virtual Key
                  chỉ có giá trị khi gửi kèm chứng chỉ mTLS phát hành cho thiết bị này.
                </p>
              </div>

              <DialogFooter className="pt-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleOpenChange(false)}
                  disabled={generateMutation.isPending}
                  className="text-xs"
                >
                  Hủy
                </Button>
                <Button
                  type="submit"
                  size="sm"
                  disabled={
                    generateMutation.isPending ||
                    !selectedClientId ||
                    activeClients.length === 0
                  }
                  className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium"
                >
                  {generateMutation.isPending ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" />
                      Đang sinh khóa...
                    </>
                  ) : (
                    <>
                      <Key className="h-3.5 w-3.5 mr-1" />
                      Cấp Virtual Key
                    </>
                  )}
                </Button>
              </DialogFooter>
            </form>
          </>
        ) : (
          /* Step 2: One-Time Secret Result */
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
              {/* Security Alert */}
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

              {/* Raw Key Display Box */}
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

              {/* CLI Command Snippet Box */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-700 flex items-center gap-1.5">
                    <Terminal className="h-3.5 w-3.5 text-blue-600" />
                    Lệnh thực thi mẫu với CLI SDK:
                  </span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleCopyCommand}
                    className="h-6 px-2 text-xs text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                  >
                    {copiedCommand ? (
                      <>
                        <Check className="h-3 w-3 mr-1 text-emerald-600" />
                        Đã chép
                      </>
                    ) : (
                      <>
                        <Copy className="h-3 w-3 mr-1 text-blue-500" />
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
                onClick={() => handleOpenChange(false)}
                className="w-full sm:w-auto text-xs"
              >
                Đã lưu an toàn & Hoàn tất
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
