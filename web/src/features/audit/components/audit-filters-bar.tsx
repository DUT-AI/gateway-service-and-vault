"use client";

import React from "react";
import { Filter, RefreshCw, X } from "lucide-react";
import type { AuditFilterParams } from "../types";

interface AuditFiltersBarProps {
  filters: AuditFilterParams;
  onFilterChange: (newFilters: Partial<AuditFilterParams>) => void;
  onReset: () => void;
  onRefresh: () => void;
  isFetching?: boolean;
}

export function AuditFiltersBar({
  filters,
  onFilterChange,
  onReset,
  onRefresh,
  isFetching,
}: AuditFiltersBarProps) {
  const hasActiveFilters = Boolean(
    filters.decision || filters.client_type || filters.error_code || filters.project_id
  );

  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-3.5 shadow-xs dark:border-slate-800 dark:bg-slate-900">
      <div className="flex flex-wrap items-center gap-2.5">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500">
          <Filter className="h-4 w-4" />
          <span>Bộ lọc:</span>
        </div>

        {/* Filter by Decision */}
        <select
          value={filters.decision || ""}
          onChange={(e) =>
            onFilterChange({ decision: e.target.value || undefined, offset: 0 })
          }
          className="rounded-lg border border-slate-200 bg-slate-50/50 px-2.5 py-1.5 text-xs font-medium text-slate-700 outline-hidden hover:bg-slate-100 focus:border-blue-500 focus:bg-white dark:border-slate-800 dark:bg-slate-800 dark:text-slate-200"
        >
          <option value="">Tất cả kết quả (ALLOW / DENY)</option>
          <option value="ALLOW">Chỉ xem: Cho phép (ALLOW)</option>
          <option value="DENY">Chỉ xem: Bị từ chối (DENY)</option>
        </select>

        {/* Filter by Client Type */}
        <select
          value={filters.client_type || ""}
          onChange={(e) =>
            onFilterChange({ client_type: e.target.value || undefined, offset: 0 })
          }
          className="rounded-lg border border-slate-200 bg-slate-50/50 px-2.5 py-1.5 text-xs font-medium text-slate-700 outline-hidden hover:bg-slate-100 focus:border-blue-500 focus:bg-white dark:border-slate-800 dark:bg-slate-800 dark:text-slate-200"
        >
          <option value="">Tất cả thiết bị (Actor)</option>
          <option value="USER_DEVICE">Thiết bị cá nhân (User Device)</option>
          <option value="APP_SERVER">Máy chủ ứng dụng (App Server)</option>
        </select>

        {/* Filter by Error Code */}
        <select
          value={filters.error_code || ""}
          onChange={(e) =>
            onFilterChange({ error_code: e.target.value || undefined, offset: 0 })
          }
          className="rounded-lg border border-slate-200 bg-slate-50/50 px-2.5 py-1.5 text-xs font-medium text-slate-700 outline-hidden hover:bg-slate-100 focus:border-blue-500 focus:bg-white dark:border-slate-800 dark:bg-slate-800 dark:text-slate-200"
        >
          <option value="">Tất cả loại lỗi vi phạm</option>
          <option value="IDENTITY_MISMATCH">Sai lệch định danh (IDENTITY_MISMATCH)</option>
          <option value="DAILY_QUOTA_EXCEEDED">Hết hạn mức ngày (DAILY_QUOTA_EXCEEDED)</option>
          <option value="CLIENT_REVOKED">Thiết bị đã thu hồi (CLIENT_REVOKED)</option>
          <option value="SERVICE_NOT_ALLOWED">Dịch vụ chưa cấp quyền (SERVICE_NOT_ALLOWED)</option>
        </select>

        {hasActiveFilters && (
          <button
            type="button"
            onClick={onReset}
            className="inline-flex items-center gap-1 rounded-lg px-2 py-1.5 text-xs font-medium text-rose-600 hover:bg-rose-50 dark:text-rose-400 dark:hover:bg-rose-950/30"
          >
            <X className="h-3.5 w-3.5" />
            Xóa bộ lọc
          </button>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onRefresh}
          disabled={isFetching}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-2xs hover:bg-slate-50 disabled:opacity-50 dark:border-slate-800 dark:bg-slate-800 dark:text-slate-200"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? "animate-spin" : ""}`} />
          <span>Làm mới</span>
        </button>
      </div>
    </div>
  );
}
