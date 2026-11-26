"use client";

import React from "react";
import { KeyRound, Shield } from "lucide-react";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { ClientsTable } from "@/features/clients";

export default function ClientsPage() {
  return (
    <div className="space-y-6">
      {/* Breadcrumbs Navigation */}
      <Breadcrumbs items={[{ label: "Thiết bị & Client" }]} />

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Quản lý thiết bị & Client mTLS
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-[#EEF3FA] px-2 py-0.5 text-[11px] font-semibold text-[#042B5F] border border-[#042B5F]/20">
              <Shield className="h-3 w-3" />
              Zero-Trust Gatekeeper
            </span>
          </div>
          <p className="text-xs text-slate-500 max-w-2xl leading-relaxed">
            Danh mục các thiết bị lập trình viên và máy chủ workload được cấp chứng
            chỉ mTLS để xác thực phần cứng khi truy cập hệ thống API Gateway.
          </p>
        </div>
      </div>

      {/* Clients Directory Table */}
      <ClientsTable />
    </div>
  );
}
