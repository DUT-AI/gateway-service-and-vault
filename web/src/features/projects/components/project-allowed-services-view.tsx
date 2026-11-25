"use client";

import React, { useState } from "react";
import { Server, Plus, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AllowedServicesTable } from "./allowed-services-table";
import { BindServiceDialog } from "./bind-service-dialog";
import { useProjectAllowedServicesQuery } from "../hooks/use-projects-queries";

export interface ProjectAllowedServicesViewProps {
  projectId: string;
}

export function ProjectAllowedServicesView({
  projectId,
}: ProjectAllowedServicesViewProps) {
  const [isBindOpen, setIsBindOpen] = useState(false);
  const { data: allowedServices = [], isLoading } =
    useProjectAllowedServicesQuery(projectId);

  const alreadyBoundIds = allowedServices.map((s) => s.service_id);

  return (
    <div className="space-y-6">
      {/* Top Banner / Actions Card */}
      <Card className="min-h-[600px] border-slate-200 bg-white shadow-xs">
        <CardHeader className="flex flex-row items-center justify-between pb-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <Server className="h-5 w-5 text-blue-600" />
              <CardTitle className="text-base font-semibold text-slate-900">
                Dịch vụ liên kết & Quota Governance
              </CardTitle>
            </div>
            <p className="text-xs text-slate-500">
              Kiểm soát các dịch vụ Upstream mà dự án được cấp phép truy cập qua
              API Gateway và thiết lập hạn mức lưu lượng (RPM / Ngày).
            </p>
          </div>

          <Button
            size="sm"
            onClick={() => setIsBindOpen(true)}
            className="text-xs bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Plus className="h-4 w-4 mr-1.5" />
            Thêm dịch vụ
          </Button>
        </CardHeader>

        <CardContent>
          {/* Quick Notice */}
          <div className="mb-4 rounded-lg bg-blue-50/60 border border-blue-200/70 p-3 flex items-start space-x-3 text-xs text-blue-800">
            <ShieldCheck className="h-4 w-4 text-blue-600 mt-0.5 shrink-0" />
            <div className="space-y-0.5">
              <p className="font-semibold">Nguyên tắc Zero-Trust Gateway:</p>
              <p className="text-slate-600">
                Chỉ những dịch vụ được khai báo trong danh sách dưới đây mới có
                thể được gọi bằng Virtual Key của dự án. Mọi yêu cầu tới API
                chưa được liên kết sẽ bị chặn ngay lập tức với mã lỗi HTTP 403.
              </p>
            </div>
          </div>

          {/* Table */}
          <AllowedServicesTable
            projectId={projectId}
            services={allowedServices}
            isLoading={isLoading}
            onOpenBindDialog={() => setIsBindOpen(true)}
          />
        </CardContent>
      </Card>

      {/* Bind Service Modal */}
      <BindServiceDialog
        projectId={projectId}
        alreadyBoundServiceIds={alreadyBoundIds}
        open={isBindOpen}
        onOpenChange={setIsBindOpen}
      />
    </div>
  );
}
