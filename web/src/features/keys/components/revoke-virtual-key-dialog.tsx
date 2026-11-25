"use client";

import React from "react";
import { AlertTriangle, Ban, Loader2, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { VirtualKey } from "../types";

export interface RevokeVirtualKeyDialogProps {
  keyToRevoke: VirtualKey | null;
  clientName?: string;
  isPending: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export function RevokeVirtualKeyDialog({
  keyToRevoke,
  clientName,
  isPending,
  onClose,
  onConfirm,
}: RevokeVirtualKeyDialogProps) {
  return (
    <Dialog
      open={Boolean(keyToRevoke)}
      onOpenChange={(open) => !open && onClose()}
    >
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-100 text-rose-700">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold text-slate-900">
                Xác nhận thu hồi Virtual Key
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500">
                Thao tác này sẽ ngắt kết nối ngay lập tức tại Gateway.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        {keyToRevoke && (
          <div className="space-y-3 pt-1 text-xs">
            <div className="rounded-xl border border-rose-200 bg-rose-50/80 p-3.5 space-y-1.5 text-rose-950">
              <p className="font-semibold flex items-center gap-1.5">
                <AlertTriangle className="h-4 w-4 text-rose-600 shrink-0" />
                Cảnh báo: Hành động không thể hoàn tác!
              </p>
              <p className="text-[11px] text-rose-800 leading-relaxed">
                Ngay sau khi xác nhận, toàn bộ ứng dụng và script đang sử dụng
                Virtual Key với prefix{" "}
                <strong className="font-mono">{keyToRevoke.key_prefix}...</strong>{" "}
                sẽ bị APISIX Gateway từ chối kết nối với mã lỗi{" "}
                <code className="font-mono bg-rose-100 px-1 py-0.5 rounded">
                  HTTP 403 Forbidden
                </code>
                .
              </p>
            </div>

            <div className="rounded-lg border border-slate-200 p-3 bg-slate-50/60 space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-500">Mã Key Prefix:</span>
                <span className="font-mono font-semibold text-slate-800">
                  {keyToRevoke.key_prefix}...
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Thiết bị ràng buộc:</span>
                <span className="font-semibold text-slate-800">
                  {clientName ?? keyToRevoke.client_id.slice(0, 12)}
                </span>
              </div>
            </div>
          </div>
        )}

        <DialogFooter className="pt-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onClose}
            disabled={isPending}
            className="text-xs"
          >
            Hủy
          </Button>
          <Button
            type="button"
            size="sm"
            onClick={onConfirm}
            disabled={isPending}
            className="bg-rose-600 hover:bg-rose-700 text-white text-xs font-medium"
          >
            {isPending ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" />
                Đang thu hồi...
              </>
            ) : (
              <>
                <Ban className="h-3.5 w-3.5 mr-1" />
                Xác nhận thu hồi ngay
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
