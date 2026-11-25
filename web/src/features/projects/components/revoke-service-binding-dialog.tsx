"use client";

import React from "react";
import { AlertTriangle, Loader2 } from "lucide-react";
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
import type { ProjectAllowedService } from "../types";
import { useUnbindServiceFromProjectMutation } from "../hooks/use-projects-queries";

export interface RevokeServiceBindingDialogProps {
  projectId: string;
  service: ProjectAllowedService | null;
  onClose: () => void;
}

export function RevokeServiceBindingDialog({
  projectId,
  service,
  onClose,
}: RevokeServiceBindingDialogProps) {
  const unbindMutation = useUnbindServiceFromProjectMutation(projectId);

  const handleConfirmRevoke = async () => {
    if (!service) return;

    try {
      await unbindMutation.mutateAsync(service.service_id);
      toast.success(
        `Đã thu hồi quyền truy cập dịch vụ ${service.service_name}`
      );
      onClose();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail;
      toast.error(detail || "Không thể thu hồi quyền dịch vụ");
    }
  };

  return (
    <Dialog open={Boolean(service)} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[420px]">
        <DialogHeader>
          <div className="flex items-center space-x-2 text-red-600">
            <AlertTriangle className="h-5 w-5" />
            <DialogTitle className="text-sm font-semibold text-slate-900">
              Xác nhận thu hồi quyền dịch vụ
            </DialogTitle>
          </div>
          <DialogDescription className="text-xs text-slate-500 pt-1">
            Bạn có chắc chắn muốn ngắt liên kết dịch vụ{" "}
            <span className="font-semibold text-slate-800">
              {service?.service_name}
            </span>{" "}
            khỏi dự án này?
          </DialogDescription>
        </DialogHeader>

        <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-xs text-red-700 space-y-1">
          <p className="font-medium">Cảnh báo bảo mật:</p>
          <p className="text-[11px] leading-relaxed">
            Tất cả các Virtual Key của dự án sẽ ngay lập tức bị từ chối (HTTP
            403 Forbidden) khi cố gắng gọi đến API này qua Gateway.
          </p>
        </div>

        <DialogFooter className="pt-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onClose}
            className="text-xs"
          >
            Hủy
          </Button>
          <Button
            size="sm"
            variant="destructive"
            onClick={handleConfirmRevoke}
            disabled={unbindMutation.isPending}
            className="text-xs"
          >
            {unbindMutation.isPending ? (
              <>
                <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                Đang thu hồi...
              </>
            ) : (
              "Xác nhận xóa quyền"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
