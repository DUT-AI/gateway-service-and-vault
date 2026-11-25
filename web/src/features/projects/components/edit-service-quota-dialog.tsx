"use client";

import React, { useState } from "react";
import { Edit2, Loader2, ShieldCheck, Zap } from "lucide-react";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { ProjectAllowedService } from "../types";
import { useUpdateServiceQuotaMutation } from "../hooks/use-projects-queries";

export interface EditServiceQuotaDialogProps {
  projectId: string;
  service: ProjectAllowedService | null;
  onClose: () => void;
}

export function EditServiceQuotaDialog({
  projectId,
  service,
  onClose,
}: EditServiceQuotaDialogProps) {
  const [editRpm, setEditRpm] = useState<number>(
    service?.rate_limit_rpm ?? 60
  );
  const [editDaily, setEditDaily] = useState<number>(
    service?.quota_daily ?? 10000
  );
  const updateQuotaMutation = useUpdateServiceQuotaMutation(projectId);

  const handleSaveQuota = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!service) return;

    if (editRpm < 1 || editDaily < 1) {
      toast.error("Hạn mức phải lớn hơn 0");
      return;
    }

    try {
      await updateQuotaMutation.mutateAsync({
        serviceId: service.service_id,
        payload: {
          rate_limit_rpm: editRpm,
          quota_daily: editDaily,
        },
      });
      toast.success(`Đã cập nhật Quota cho ${service.service_name}`);
      onClose();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail;
      toast.error(detail || "Không thể cập nhật hạn mức quota");
    }
  };

  return (
    <Dialog open={Boolean(service)} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[400px]">
        <DialogHeader>
          <div className="flex items-center space-x-2 text-blue-600">
            <Edit2 className="h-4 w-4" />
            <DialogTitle className="text-sm font-semibold text-slate-900">
              Điều chỉnh Quota: {service?.service_name}
            </DialogTitle>
          </div>
          <DialogDescription className="text-xs text-slate-500">
            Cập nhật giới hạn tốc độ và hạn mức số lượng request hàng ngày.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSaveQuota} className="space-y-4 py-2">
          <div className="space-y-1.5">
            <Label className="text-xs font-semibold text-slate-700 flex items-center space-x-1">
              <Zap className="h-3.5 w-3.5 text-amber-500" />
              <span>Giới hạn RPM (Requests/phút)</span>
            </Label>
            <Input
              type="number"
              min={1}
              max={100000}
              value={editRpm}
              onChange={(e) => setEditRpm(Number(e.target.value))}
              className="text-xs"
            />
          </div>

          <div className="space-y-1.5">
            <Label className="text-xs font-semibold text-slate-700 flex items-center space-x-1">
              <ShieldCheck className="h-3.5 w-3.5 text-blue-500" />
              <span>Hạn mức ngày (Requests/ngày)</span>
            </Label>
            <Input
              type="number"
              min={1}
              max={10000000}
              value={editDaily}
              onChange={(e) => setEditDaily(Number(e.target.value))}
              className="text-xs"
            />
          </div>

          <DialogFooter className="pt-3">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={onClose}
              className="text-xs"
            >
              Hủy
            </Button>
            <Button
              type="submit"
              size="sm"
              disabled={updateQuotaMutation.isPending}
              className="text-xs bg-blue-600 hover:bg-blue-700 text-white"
            >
              {updateQuotaMutation.isPending ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                  Đang lưu...
                </>
              ) : (
                "Lưu thay đổi"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
