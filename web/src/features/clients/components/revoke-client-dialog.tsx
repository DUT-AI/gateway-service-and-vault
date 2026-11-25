"use client";

import React from "react";
import { AlertTriangle, Ban, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { Client } from "../types";

export interface RevokeClientDialogProps {
  client: Client | null;
  isPending: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export function RevokeClientDialog({
  client,
  isPending,
  onClose,
  onConfirm,
}: RevokeClientDialogProps) {
  return (
    <Dialog open={!!client} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-2 text-rose-600 mb-1">
            <AlertTriangle className="h-5 w-5" />
            <DialogTitle>Xác nhận thu hồi thiết bị mTLS</DialogTitle>
          </div>
          <DialogDescription className="text-xs text-slate-500">
            Hành động này sẽ vô hiệu hóa vĩnh viễn thiết bị phần cứng này và lập
            tức thu hồi toàn bộ Virtual Access Keys đang hoạt động liên kết với
            thiết bị này.
          </DialogDescription>
        </DialogHeader>

        {client && (
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5 my-2">
            <div className="flex justify-between">
              <span className="text-slate-500">Thiết bị:</span>
              <span className="font-semibold text-slate-900">{client.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Fingerprint:</span>
              <span className="font-mono text-slate-700">
                {client.cert_fingerprint.slice(0, 16)}...
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Loại:</span>
              <span className="font-medium text-slate-800">
                {client.client_type === "USER_DEVICE"
                  ? "Developer PC"
                  : "Workload Server"}
              </span>
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
