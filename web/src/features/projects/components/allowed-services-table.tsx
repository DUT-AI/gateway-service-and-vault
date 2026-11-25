"use client";

import React, { useState } from "react";
import { toast } from "sonner";
import {
  AlertTriangle,
  Server,
  Trash2,
  Edit2,
  Copy,
  Plus,
  Loader2,
  CheckCircle2,
  XCircle,
  Zap,
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
import type { ProjectAllowedService } from "../types";
import { EditServiceQuotaDialog } from "./edit-service-quota-dialog";
import { RevokeServiceBindingDialog } from "./revoke-service-binding-dialog";

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
  const [revokingService, setRevokingService] =
    useState<ProjectAllowedService | null>(null);

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success(`Đã sao chép ${label} vào bộ nhớ tạm`);
    } catch {
      toast.error("Không thể sao chép");
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
                    onClick={() => setEditingService(svc)}
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

      <EditServiceQuotaDialog
        key={editingService?.service_id ?? "closed"}
        projectId={projectId}
        service={editingService}
        onClose={() => setEditingService(null)}
      />

      <RevokeServiceBindingDialog
        projectId={projectId}
        service={revokingService}
        onClose={() => setRevokingService(null)}
      />
    </>
  );
}
