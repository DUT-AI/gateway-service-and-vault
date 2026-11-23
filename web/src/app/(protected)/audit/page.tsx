"use client";

import React, { useState } from "react";
import { ShieldAlert, ShieldCheck } from "lucide-react";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import {
  AuditFiltersBar,
  AuditLogsTable,
  SecurityAlertsBanner,
  useAuditEventsQuery,
  useSecurityAlertsQuery,
  type AuditFilterParams,
} from "@/features/audit";

export default function AuditPage() {
  const [filters, setFilters] = useState<AuditFilterParams>({
    limit: 50,
    offset: 0,
  });

  const {
    data: eventsData,
    isLoading: isEventsLoading,
    isFetching: isEventsFetching,
    refetch: refetchEvents,
  } = useAuditEventsQuery(filters);

  const {
    data: alertsData,
    isLoading: isAlertsLoading,
    refetch: refetchAlerts,
  } = useSecurityAlertsQuery();

  const handleFilterChange = (newFilters: Partial<AuditFilterParams>) => {
    setFilters((prev) => ({
      ...prev,
      ...newFilters,
    }));
  };

  const handleResetFilters = () => {
    setFilters({
      limit: 50,
      offset: 0,
    });
  };

  const handleRefresh = () => {
    refetchEvents();
    refetchAlerts();
  };

  const handlePageChange = (newOffset: number) => {
    setFilters((prev) => ({
      ...prev,
      offset: newOffset,
    }));
  };

  return (
    <div className="space-y-6">
      {/* Breadcrumbs Navigation */}
      <Breadcrumbs items={[{ label: "Nhật ký an ninh" }]} />

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5 dark:border-slate-800">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
              Nhật ký kiểm toán an ninh & Cảnh báo
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800">
              <ShieldCheck className="h-3.5 w-3.5" />
              Bất biến (Immutable Audit)
            </span>
          </div>
          <p className="text-xs text-slate-500 max-w-2xl leading-relaxed dark:text-slate-400">
            Theo dõi toàn diện các quyết định cấp phép và từ chối truy cập qua API Gateway,
            phân biệt chính xác giữa thiết bị cá nhân (User Device) và máy chủ (App Server),
            đồng thời phát hiện tự động các hành vi vi phạm an ninh lặp lại.
          </p>
        </div>
      </div>

      {/* Security Alerts Banner */}
      <SecurityAlertsBanner
        alerts={alertsData?.alerts || []}
        isLoading={isAlertsLoading}
      />

      {/* Filters Bar */}
      <AuditFiltersBar
        filters={filters}
        onFilterChange={handleFilterChange}
        onReset={handleResetFilters}
        onRefresh={handleRefresh}
        isFetching={isEventsFetching}
      />

      {/* Audit Logs Table */}
      <AuditLogsTable
        events={eventsData?.items || []}
        total={eventsData?.total || 0}
        limit={filters.limit || 50}
        offset={filters.offset || 0}
        isLoading={isEventsLoading}
        onPageChange={handlePageChange}
      />
    </div>
  );
}
