"use client";

import React, { useState } from "react";
import { toast } from "sonner";
import {
  Server,
  Zap,
  ShieldCheck,
  Trash2,
  Edit2,
  Copy,
  Plus,
  AlertTriangle,
  Loader2,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { ProjectAllowedService } from "../types";
import {
  useUnbindServiceFromProjectMutation,
  useUpdateServiceQuotaMutation,
} from "../hooks/use-projects-queries";

export interface AllowedServicesTableProps {
  projectId: string;
  services: ProjectAllowedService[];
  isLoading: boolean;
  onOpenBindDialog: () => void;
}

export function AllowedServicesTable({
  projectId,
  services,
  isLoading,
  onOpenBindDialog,
}: AllowedServicesTableProps) {
  const [editingService, setEditingService] =
    useState<ProjectAllowedService | null>(null);
  const [editRpm, setEditRpm] = useState<number>(60);
  const [editDaily, setEditDaily] = useState<number>(10000);

  const [revokingService, setRevokingService] =
    useState<ProjectAllowedService | null>(null);

  const unbindMutation = useUnbindServiceFromProjectMutation(projectId);
  const updateQuotaMutation = useUpdateServiceQuotaMutation(projectId);

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success(`Đã sao chép ${label} vào bộ nhớ tạm`);
    } catch {
      toast.error("Không thể sao chép");
    }
  };

  const handleStartEdit = (svc: ProjectAllowedService) => {
    setEditingService(svc);
    setEditRpm(svc.rate_limit_rpm);
    setEditDaily(svc.quota_daily);
  };

  const handleSaveQuota = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingService) return;

    if (editRpm < 1 || editDaily < 1) {
      toast.error("Hạn mức phải lớn hơn 0");
      return;
    }

    try {
      await updateQuotaMutation.mutateAsync({
        serviceId: editingService.service_id,
        payload: {
          rate_limit_rpm: editRpm,
          quota_daily: editDaily,
        },
      });
      toast.success(`Đã cập nhật Quota cho ${editingService.service_name}`);
      setEditingService(null);
    } catch (err: any) {
      toast.error(
        err?.response?.data?.detail || "Không thể cập nhật hạn mức quota"
      );
    }
  };

  const handleConfirmRevoke = async () => {
    if (!revokingService) return;

    try {
      await unbindMutation.mutateAsync(revokingService.service_id);
      toast.success(
        `Đã thu hồi quyền truy cập dịch vụ ${revokingService.service_name}`
      );
      setRevokingService(null);
    } catch (err: any) {
      toast.error(
        err?.response?.data?.detail || "Không thể thu hồi quyền dịch vụ"
      );
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 space-y-3 bg-white rounded-xl border border-slate-200">
        <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
        <p className="text-xs text-slate-500">
          Đang tải danh sách dịch vụ liên kết...
        </p>
      </div>
    );
  }

  if (services.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-xl border border-dashed border-slate-300">
        <div className="h-12 w-12 rounded-full bg-blue-50 flex items-center justify-center mb-4">
          <Server className="h-6 w-6 text-blue-600" />
        </div>
        <h3 className="text-sm font-semibold text-slate-900">
          Chưa có dịch vụ upstream nào được liên kết
        </h3>
        <p className="text-xs text-slate-500 max-w-sm mt-1 mb-5">
          Theo nguyên tắc Zero-Trust, dự án chỉ có thể gọi đến các API upstream
          sau khi được cấp quyền và gán chính sách hạn mức Quota.
        </p>
        <Button
          size="sm"
          onClick={onOpenBindDialog}
          className="text-xs bg-blue-600 hover:bg-blue-700 text-white"
        >
          <Plus className="h-3.5 w-3.5 mr-1.5" />
          Thêm dịch vụ đầu tiên
        </Button>
      </div>
    );
  }

  return (
    <>
      <div className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-xs">
        <Table>
          <TableHeader className="bg-slate-50">
            <TableRow>
              <TableHead className="text-[11px] font-semibold text-slate-600 uppercase">
                Dịch vụ Upstream
              </TableHead>
              <TableHead className="text-[11px] font-semibold text-slate-600 uppercase">
                Endpoint URL
              </TableHead>
              <TableHead className="text-[11px] font-semibold text-slate-600 uppercase">
                Xác thực
              </TableHead>
              <TableHead className="text-[11px] font-semibold text-slate-600 uppercase">
                Giới hạn RPM
              </TableHead>
              <TableHead className="text-[11px] font-semibold text-slate-600 uppercase">
                Hạn mức ngày
              </TableHead>
              <TableHead className="text-[11px] font-semibold text-slate-600 uppercase">
                Trạng thái
              </TableHead>
              <TableHead className="text-[11px] font-semibold text-slate-600 uppercase text-right">
                Thao tác
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {services.map((svc) => (
              <TableRow key={svc.service_id} className="hover:bg-slate-50/50">
                {/* Service Name & Slug */}
                <TableCell>
                  <div className="flex flex-col">
                    <span className="text-xs font-semibold text-slate-900 flex items-center">
                      <Server className="h-3.5 w-3.5 mr-1.5 text-blue-600" />
                      {svc.service_name}
                    </span>
                    <span className="font-mono text-[10px] text-slate-500 mt-0.5">
                      {svc.service_slug}
                    </span>
                  </div>
                </TableCell>

                {/* Base URL */}
                <TableCell>
                  <div className="flex items-center space-x-1.5 max-w-[220px]">
                    <span
                      className="font-mono text-[11px] text-slate-700 truncate"
                      title={svc.base_url}
                    >
                      {svc.base_url}
                    </span>
                    <button
                      onClick={() =>
                        copyToClipboard(svc.base_url, "Endpoint URL")
                      }
                      className="text-slate-400 hover:text-slate-600 p-0.5 rounded-sm"
                      title="Sao chép URL"
                    >
                      <Copy className="h-3 w-3" />
                    </button>
                  </div>
                </TableCell>

                {/* Auth Type */}
                <TableCell>
                  <Badge
                    variant="outline"
                    className="text-[10px] font-mono uppercase bg-slate-50 text-slate-700"
                  >
                    {svc.auth_type}
                  </Badge>
                </TableCell>

                {/* RPM */}
                <TableCell>
                  <div className="flex items-center space-x-1 text-xs font-semibold text-amber-700">
                    <Zap className="h-3 w-3 text-amber-500" />
                    <span>{svc.rate_limit_rpm.toLocaleString()} RPM</span>
                  </div>
                </TableCell>

                {/* Daily Quota & Usage Progress */}
                <TableCell>
                  <div className="flex flex-col space-y-1.5 min-w-[155px]">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-800">
                        {(svc.usage_today ?? 0).toLocaleString()} /{" "}
                        {svc.quota_daily.toLocaleString()}
                      </span>
                      <span
                        className={`text-[10px] font-bold ${
                          (svc.usage_percentage ?? 0) >= 100
                            ? "text-rose-600"
                            : (svc.usage_percentage ?? 0) >= 80
                              ? "text-amber-600"
                              : "text-emerald-600"
                        }`}
                      >
                        {svc.usage_percentage ?? 0}%
                      </span>
                    </div>
                    {/* Progress track */}
                    <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-300 ${
                          (svc.usage_percentage ?? 0) >= 100
                            ? "bg-rose-500"
                            : (svc.usage_percentage ?? 0) >= 80
                              ? "bg-amber-500"
                              : "bg-emerald-500"
                        }`}
                        style={{
                          width: `${Math.min(svc.usage_percentage ?? 0, 100)}%`,
                        }}
                      />
                    </div>
                    {(svc.usage_percentage ?? 0) >= 100 && (
                      <span className="text-[9px] font-semibold text-rose-600 flex items-center">
                        <AlertTriangle className="h-2.5 w-2.5 mr-0.5 inline" />
                        Hết hạn mức ngày
                      </span>
                    )}
                  </div>
                </TableCell>

                {/* Active Status */}
                <TableCell>
                  {svc.is_service_active ? (
                    <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 text-[10px] font-medium flex items-center w-fit gap-1">
                      <CheckCircle2 className="h-3 w-3" />
                      Hoạt động
                    </Badge>
                  ) : (
                    <Badge className="bg-red-50 text-red-700 border-red-200 text-[10px] font-medium flex items-center w-fit gap-1">
                      <XCircle className="h-3 w-3" />
                      Tạm ngưng
                    </Badge>
                  )}
                </TableCell>

                {/* Action Buttons */}
                <TableCell className="text-right space-x-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleStartEdit(svc)}
                    className="h-7 px-2 text-xs text-slate-600 hover:text-blue-700"
                    title="Chỉnh sửa Quota"
                  >
                    <Edit2 className="h-3.5 w-3.5 mr-1" />
                    Sửa
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setRevokingService(svc)}
                    className="h-7 px-2 text-xs text-red-600 hover:bg-red-50 hover:text-red-700"
                    title="Thu hồi quyền truy cập"
                  >
                    <Trash2 className="h-3.5 w-3.5 mr-1" />
                    Xóa quyền
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Edit Quota Dialog */}
      {editingService && (
        <Dialog
          open={Boolean(editingService)}
          onOpenChange={(open) => !open && setEditingService(null)}
        >
          <DialogContent className="sm:max-w-[400px]">
            <DialogHeader>
              <div className="flex items-center space-x-2 text-blue-600">
                <Edit2 className="h-4 w-4" />
                <DialogTitle className="text-sm font-semibold text-slate-900">
                  Điều chỉnh Quota: {editingService.service_name}
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
                  onClick={() => setEditingService(null)}
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
      )}

      {/* Revoke Confirmation Dialog */}
      {revokingService && (
        <Dialog
          open={Boolean(revokingService)}
          onOpenChange={(open) => !open && setRevokingService(null)}
        >
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
                  {revokingService.service_name}
                </span>{" "}
                khỏi dự án này?
              </DialogDescription>
            </DialogHeader>

            <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-xs text-red-700 space-y-1">
              <p className="font-medium">Cảnh báo bảo mật:</p>
              <p className="text-[11px] leading-relaxed">
                Tất cả các Virtual Key của dự án sẽ ngay lập tức bị từ chối
                (HTTP 403 Forbidden) khi cố gắng gọi đến API này qua Gateway.
              </p>
            </div>

            <DialogFooter className="pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setRevokingService(null)}
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
      )}
    </>
  );
}
