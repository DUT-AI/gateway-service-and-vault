"use client";

import React, { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  Laptop,
  Server,
  ChevronLeft,
  ChevronRight,
  Code2,
  X,
  FileQuestion,
} from "lucide-react";
import type { AuditEvent } from "../types";

interface AuditLogsTableProps {
  events: AuditEvent[];
  total: number;
  limit: number;
  offset: number;
  isLoading?: boolean;
  onPageChange: (newOffset: number) => void;
}

export function AuditLogsTable({
  events,
  total,
  limit,
  offset,
  isLoading,
  onPageChange,
}: AuditLogsTableProps) {
  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null);

  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.max(1, Math.ceil(total / limit));

  if (isLoading) {
    return (
      <div className="flex min-h-[300px] items-center justify-center rounded-xl border border-slate-200 bg-white p-8 dark:border-slate-800 dark:bg-slate-900">
        <div className="flex flex-col items-center gap-2">
          <div className="h-7 w-7 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
          <p className="text-xs text-slate-500">Đang tải nhật ký kiểm toán...</p>
        </div>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="flex min-h-[300px] flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 bg-white p-8 text-center dark:border-slate-800 dark:bg-slate-900">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 text-slate-400 dark:bg-slate-800">
          <FileQuestion className="h-6 w-6" />
        </div>
        <h3 className="mt-3 text-sm font-semibold text-slate-800 dark:text-slate-200">
          Chưa có nhật ký truy cập
        </h3>
        <p className="mt-1 text-xs text-slate-500">
          Không tìm thấy sự kiện nào khớp với điều kiện lọc hiện tại.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xs dark:border-slate-800 dark:bg-slate-900">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-200 bg-slate-50/75 text-[11px] font-semibold tracking-wider text-slate-500 uppercase dark:border-slate-800 dark:bg-slate-800/50 dark:text-slate-400">
              <tr>
                <th className="px-4 py-3">Thời gian</th>
                <th className="px-4 py-3">Đối tượng (Actor)</th>
                <th className="px-4 py-3">Hành động</th>
                <th className="px-4 py-3">Kết quả</th>
                <th className="px-4 py-3">Mã lỗi / Lý do</th>
                <th className="px-4 py-3">Client IP</th>
                <th className="px-4 py-3 text-right">Chi tiết</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {events.map((event) => {
                const isAllow = event.decision === "ALLOW";
                const isAppServer = event.client_type === "APP_SERVER";

                return (
                  <tr
                    key={event.id}
                    className="transition-colors hover:bg-slate-50/60 dark:hover:bg-slate-800/40"
                  >
                    {/* Timestamp */}
                    <td className="px-4 py-3 whitespace-nowrap text-slate-600 dark:text-slate-300">
                      <div className="font-medium text-slate-900 dark:text-white">
                        {new Date(event.timestamp).toLocaleTimeString("vi-VN")}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {new Date(event.timestamp).toLocaleDateString("vi-VN")}
                      </div>
                    </td>

                    {/* Actor Type & Actor ID */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        {isAppServer ? (
                          <span className="inline-flex items-center gap-1 rounded-md bg-purple-50 px-2 py-0.5 text-[11px] font-medium text-purple-700 ring-1 ring-purple-600/20 ring-inset dark:bg-purple-950/40 dark:text-purple-300">
                            <Server className="h-3 w-3" />
                            App Server
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 rounded-md bg-blue-50 px-2 py-0.5 text-[11px] font-medium text-blue-700 ring-1 ring-blue-600/20 ring-inset dark:bg-blue-950/40 dark:text-blue-300">
                            <Laptop className="h-3 w-3" />
                            User Device
                          </span>
                        )}
                      </div>
                      <div className="mt-1 font-mono text-[11px] text-slate-500 truncate max-w-[150px]">
                        {event.actor_id}
                      </div>
                    </td>

                    {/* Action */}
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="font-mono text-[11px] font-semibold text-slate-700 dark:text-slate-300">
                        {event.action}
                      </span>
                    </td>

                    {/* Decision */}
                    <td className="px-4 py-3 whitespace-nowrap">
                      {isAllow ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 ring-1 ring-emerald-600/20 ring-inset dark:bg-emerald-950/40 dark:text-emerald-300">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          ALLOW
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-semibold text-rose-700 ring-1 ring-rose-600/20 ring-inset dark:bg-rose-950/40 dark:text-rose-300">
                          <XCircle className="h-3.5 w-3.5" />
                          DENY
                        </span>
                      )}
                    </td>

                    {/* Error code */}
                    <td className="px-4 py-3 whitespace-nowrap">
                      {event.error_code ? (
                        <span
                          className={`inline-flex rounded-md px-2 py-0.5 text-[11px] font-mono font-medium ${
                            event.error_code === "IDENTITY_MISMATCH"
                              ? "bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300"
                              : event.error_code === "DAILY_QUOTA_EXCEEDED"
                              ? "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300"
                              : "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                          }`}
                        >
                          {event.error_code}
                        </span>
                      ) : (
                        <span className="text-slate-400">-</span>
                      )}
                    </td>

                    {/* Client IP */}
                    <td className="px-4 py-3 whitespace-nowrap font-mono text-[11px] text-slate-600 dark:text-slate-400">
                      {event.client_ip || "—"}
                    </td>

                    {/* Details modal button */}
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      <button
                        type="button"
                        onClick={() => setSelectedEvent(event)}
                        className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:border-slate-800 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
                      >
                        <Code2 className="h-3.5 w-3.5" />
                        <span>Xem</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="flex items-center justify-between border-t border-slate-200 px-4 py-3 dark:border-slate-800">
          <p className="text-xs text-slate-500">
            Hiển thị <span className="font-semibold text-slate-700 dark:text-slate-300">{offset + 1}</span> -{" "}
            <span className="font-semibold text-slate-700 dark:text-slate-300">
              {Math.min(offset + limit, total)}
            </span>{" "}
            trong tổng số <span className="font-semibold text-slate-700 dark:text-slate-300">{total}</span> sự kiện
          </p>

          <div className="flex items-center gap-1.5">
            <button
              type="button"
              disabled={offset === 0}
              onClick={() => onPageChange(Math.max(0, offset - limit))}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40 dark:border-slate-800 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              Trước
            </button>
            <span className="px-2 text-xs font-medium text-slate-600 dark:text-slate-400">
              {currentPage} / {totalPages}
            </span>
            <button
              type="button"
              disabled={offset + limit >= total}
              onClick={() => onPageChange(offset + limit)}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40 dark:border-slate-800 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              Sau
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Metadata Detail Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-xl dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3 dark:border-slate-800">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                  Chi tiết Sự kiện Kiểm toán
                </h3>
                <p className="font-mono text-xs text-slate-400">{selectedEvent.id}</p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedEvent(null)}
                className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="mt-4 space-y-3">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-slate-400">Thời gian:</span>
                  <p className="font-medium text-slate-800 dark:text-slate-200">
                    {new Date(selectedEvent.timestamp).toLocaleString("vi-VN")}
                  </p>
                </div>
                <div>
                  <span className="text-slate-400">Quyết định:</span>
                  <p
                    className={`font-bold ${
                      selectedEvent.decision === "ALLOW"
                        ? "text-emerald-600"
                        : "text-rose-600"
                    }`}
                  >
                    {selectedEvent.decision}
                  </p>
                </div>
                <div>
                  <span className="text-slate-400">Actor ID:</span>
                  <p className="font-mono text-slate-800 dark:text-slate-200 truncate">
                    {selectedEvent.actor_id}
                  </p>
                </div>
                <div>
                  <span className="text-slate-400">Dự án (Project ID):</span>
                  <p className="font-mono text-slate-800 dark:text-slate-200 truncate">
                    {selectedEvent.project_id}
                  </p>
                </div>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-500">
                  Dữ liệu Metadata (JSON):
                </span>
                <pre className="mt-1 max-h-56 overflow-auto rounded-lg bg-slate-950 p-3 font-mono text-xs text-emerald-400">
                  {JSON.stringify(selectedEvent.metadata || {}, null, 2)}
                </pre>
              </div>
            </div>

            <div className="mt-5 flex justify-end">
              <button
                type="button"
                onClick={() => setSelectedEvent(null)}
                className="rounded-lg bg-slate-900 px-4 py-2 text-xs font-medium text-white hover:bg-slate-800 dark:bg-white dark:text-slate-900"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
