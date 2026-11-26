"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ExternalLink,
  Key,
  KeyRound,
  Loader2,
  Plus,
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
import { NativeSelect } from "@/components/ui/native-select";
import { useUserOptionsQuery } from "@/features/vault/hooks/use-user-options-query";
import {
  useGenerateKeyMutation,
  useProjectAvailableClientsQuery,
} from "../hooks/use-keys-queries";
import { GenerateKeyResultStep } from "./generate-key-result-step";
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
  const { data: clients, isLoading: clientsLoading } =
    useProjectAvailableClientsQuery(projectId, open);
  const { data: userOptions } = useUserOptionsQuery();
  const generateMutation = useGenerateKeyMutation(projectId);

  const usersMap = useMemo(() => {
    const map = new Map<string, { name: string; email: string }>();
    if (userOptions) {
      for (const u of userOptions) {
        map.set(String(u.id), { name: u.name, email: u.email });
      }
    }
    return map;
  }, [userOptions]);

  const [selectedClientId, setSelectedClientId] = useState<string>("");
  const [step, setStep] = useState<"FORM" | "RESULT">("FORM");
  const [result, setResult] = useState<GenerateKeyResult | null>(null);
  const [mountTime] = useState<number>(() => Date.now());

  // Filter only active, non-revoked, and unexpired client devices
  const activeClients = (clients ?? []).filter((client) => {
    if (client.is_revoked) return false;
    const isExpired = new Date(client.expires_at).getTime() < mountTime;
    return !isExpired;
  });

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      setStep("FORM");
      setResult(null);
      setSelectedClientId("");
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
                    className="inline-flex items-center text-[11px] text-[#042B5F] hover:text-[#031F46] font-medium"
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
                      Thành viên dự án cần tự đăng ký ít nhất một thiết bị mTLS đang
                      hoạt động tại mục Thiết bị & Client trước khi có thể cấp phát
                      Virtual Key.
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
                  <NativeSelect
                    id="client-device"
                    value={selectedClientId}
                    onChange={(e) => setSelectedClientId(e.target.value)}
                  >
                    <option value="">-- Chọn thiết bị mTLS của thành viên --</option>
                    {activeClients.map((client) => {
                      const isDev = client.client_type === "USER_DEVICE";
                      const fpSnippet = client.cert_fingerprint.slice(0, 14);
                      const owner = usersMap.get(String(client.owner_id));
                      const ownerLabel = owner
                        ? `${owner.name} (${owner.email})`
                        : `User #${client.owner_id}`;
                      return (
                        <option key={client.id} value={client.id}>
                          {isDev ? "💻" : "🖥️"} {client.name} — {ownerLabel} (
                          {isDev ? "Dev PC" : "Workload Server"} - FP: {fpSnippet}
                          ...)
                        </option>
                      );
                    })}
                  </NativeSelect>
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
          <GenerateKeyResultStep
            result={result}
            onDone={() => handleOpenChange(false)}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}
