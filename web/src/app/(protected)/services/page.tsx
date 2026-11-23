"use client";

import React from "react";
import { Globe, Server, Shield } from "lucide-react";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { ServicesTable } from "@/features/services";

export default function ServicesPage() {
  return (
    <div className="space-y-6">
      {/* Breadcrumbs Navigation */}
      <Breadcrumbs items={[{ label: "Dịch vụ hệ thống" }]} />

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Quản lý dịch vụ Upstream
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2 py-0.5 text-[11px] font-semibold text-blue-700 border border-blue-200">
              <Shield className="h-3 w-3" />
              Reverse Proxy & Credential Injection
            </span>
          </div>
          <p className="text-xs text-slate-500 max-w-2xl leading-relaxed">
            Khai báo và bảo vệ các điểm cuối dịch vụ đối tác (OpenAI, Payment API,
            ERP,...). Gateway sẽ tự động tiêm khóa bảo mật đã mã hóa vào các request
            chuyển tiếp.
          </p>
        </div>
      </div>

      {/* Services Directory Table */}
      <ServicesTable />
    </div>
  );
}
