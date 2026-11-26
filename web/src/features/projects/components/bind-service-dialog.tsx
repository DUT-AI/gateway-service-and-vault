"use client";

import React, { useState } from "react";
import { toast } from "sonner";
import { Server, Zap, ShieldCheck, Loader2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useServicesQuery } from "@/features/services";
import { useBindServiceToProjectMutation } from "../hooks/use-projects-queries";

export interface BindServiceDialogProps {
  projectId: string;
  alreadyBoundServiceIds: string[];
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function BindServiceDialog({
  projectId,
  alreadyBoundServiceIds,
  open,
  onOpenChange,
}: BindServiceDialogProps) {
  const [selectedServiceId, setSelectedServiceId] = useState<string>("");
  const [rateLimitRpm, setRateLimitRpm] = useState<number>(60);
  const [quotaDaily, setQuotaDaily] = useState<number>(10000);

  const { data: allServices = [], isLoading: isLoadingServices } =
    useServicesQuery();
  const bindMutation = useBindServiceToProjectMutation(projectId);

  // Filter out services that are already bound
  const availableServices = allServices.filter(
    (svc) => !alreadyBoundServiceIds.includes(svc.id)
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedServiceId) {
      toast.error("Vui lòng chọn dịch vụ upstream cần liên kết");
      return;
    }

    if (rateLimitRpm < 1) {
      toast.error("Giới hạn RPM phải lớn hơn 0");
      return;
    }

    if (quotaDaily < 1) {
      toast.error("Hạn mức ngày phải lớn hơn 0");
      return;
    }

    try {
      await bindMutation.mutateAsync({
        service_id: selectedServiceId,
        rate_limit_rpm: rateLimitRpm,
        quota_daily: quotaDaily,
      });

      toast.success("Liên kết dịch vụ và thiết lập Quota thành công!");
      setSelectedServiceId("");
      setRateLimitRpm(60);
      setQuotaDaily(10000);
      onOpenChange(false);
    } catch (err: any) {
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        "Không thể liên kết dịch vụ vào dự án";
      toast.error(msg);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <div className="flex items-center space-x-2 text-[#042B5F]">
            <Server className="h-5 w-5" />
            <DialogTitle className="text-base font-semibold text-slate-900">
              Cấp quyền Dịch vụ Upstream cho Dự án
            </DialogTitle>
          </div>
          <DialogDescription className="text-xs text-slate-500">
            Cho phép dự án gọi đến API upstream qua API Gateway và áp dụng chính
            sách giới hạn lưu lượng (Quota Governance).
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          {/* Select Upstream Service */}
          <div className="space-y-1.5">
            <Label className="text-xs font-semibold text-slate-700">
              Dịch vụ Upstream Catalog <span className="text-red-500">*</span>
            </Label>
            {isLoadingServices ? (
              <div className="flex items-center space-x-2 text-xs text-slate-400 py-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Đang tải danh mục dịch vụ...</span>
              </div>
            ) : availableServices.length === 0 ? (
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
                Tất cả các dịch vụ trong hệ thống đã được liên kết với dự án này
                hoặc chưa có dịch vụ nào được khai báo.
              </div>
            ) : (
              <Select
                value={selectedServiceId}
                onValueChange={(val) => setSelectedServiceId(val || "")}
              >
                <SelectTrigger className="w-full text-xs">
                  <SelectValue placeholder="-- Chọn dịch vụ upstream --" />
                </SelectTrigger>
                <SelectContent>
                  {availableServices.map((svc) => (
                    <SelectItem
                      key={svc.id}
                      value={svc.id}
                      className="text-xs py-2"
                    >
                      <div className="flex flex-col">
                        <span className="font-semibold text-slate-900">
                          {svc.name}
                        </span>
                        <span className="font-mono text-[10px] text-slate-500">
                          {svc.base_url} ({svc.auth_type})
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>

          {/* Quota Policy Controls */}
          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="space-y-1.5">
              <Label className="text-xs font-semibold text-slate-700 flex items-center space-x-1">
                <Zap className="h-3.5 w-3.5 text-amber-500" />
                <span>Giới hạn RPM</span>
              </Label>
              <Input
                type="number"
                min={1}
                max={100000}
                value={rateLimitRpm}
                onChange={(e) => setRateLimitRpm(Number(e.target.value))}
                className="text-xs"
                placeholder="60"
              />
              <p className="text-[10px] text-slate-400">
                Số request tối đa mỗi phút (Requests/min).
              </p>
            </div>

            <div className="space-y-1.5">
              <Label className="text-xs font-semibold text-slate-700 flex items-center space-x-1">
                <ShieldCheck className="h-3.5 w-3.5 text-[#042B5F]" />
                <span>Hạn mức ngày</span>
              </Label>
              <Input
                type="number"
                min={1}
                max={10000000}
                value={quotaDaily}
                onChange={(e) => setQuotaDaily(Number(e.target.value))}
                className="text-xs"
                placeholder="10000"
              />
              <p className="text-[10px] text-slate-400">
                Tổng request tối đa mỗi ngày (Reset 00:00 UTC).
              </p>
            </div>
          </div>

          <DialogFooter className="pt-4">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => onOpenChange(false)}
              className="text-xs"
            >
              Hủy
            </Button>
            <Button
              type="submit"
              size="sm"
              disabled={
                bindMutation.isPending ||
                !selectedServiceId ||
                availableServices.length === 0
              }
              className="text-xs bg-[#042B5F] hover:bg-[#031F46] text-white"
            >
              {bindMutation.isPending ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                  Đang liên kết...
                </>
              ) : (
                "Xác nhận liên kết"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
