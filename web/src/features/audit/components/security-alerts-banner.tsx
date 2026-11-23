"use client";

import React from "react";
import { AlertTriangle, ShieldAlert, Clock, Laptop, Activity } from "lucide-react";
import type { SecurityAlert } from "../types";

interface SecurityAlertsBannerProps {
  alerts: SecurityAlert[];
  isLoading?: boolean;
}

export function SecurityAlertsBanner({
  alerts,
  isLoading,
}: SecurityAlertsBannerProps) {
  if (isLoading || !alerts || alerts.length === 0) {
    return null;
  }

  return (
    <div className="mb-6 space-y-3">
      {alerts.map((alert) => (
        <div
          key={alert.alert_id}
          className="relative overflow-hidden rounded-xl border border-rose-200 bg-rose-50/80 p-4.5 shadow-xs transition-all dark:border-rose-900/50 dark:bg-rose-950/20"
        >
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-rose-600 text-white shadow-xs">
                <ShieldAlert className="h-5 w-5" />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="inline-flex items-center gap-1 rounded-md bg-rose-100 px-2 py-0.5 text-xs font-bold text-rose-700 dark:bg-rose-900/40 dark:text-rose-300">
                    <AlertTriangle className="h-3 w-3" />
                    CẢNH BÁO BẢO MẬT: {alert.anomaly_type}
                  </span>
                  <span className="rounded-md bg-rose-600 px-2 py-0.5 text-xs font-semibold text-white">
                    {alert.severity}
                  </span>
                  <span className="inline-flex items-center gap-1 text-xs text-rose-600 font-medium dark:text-rose-400">
                    <Activity className="h-3.5 w-3.5" />
                    {alert.event_count} vi phạm liên tiếp
                  </span>
                </div>
                <p className="mt-1.5 text-sm font-medium text-slate-800 dark:text-slate-200">
                  {alert.description}
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500 dark:text-slate-400">
                  {alert.actor_id && (
                    <span className="inline-flex items-center gap-1">
                      <Laptop className="h-3.5 w-3.5 text-slate-400" />
                      Client: <code className="font-mono text-slate-700 dark:text-slate-300">{alert.actor_id}</code>
                    </span>
                  )}
                  {alert.client_ip && (
                    <span>
                      IP nguồn: <code className="font-mono text-slate-700 dark:text-slate-300">{alert.client_ip}</code>
                    </span>
                  )}
                  <span className="inline-flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5 text-slate-400" />
                    Lần cuối: {new Date(alert.last_seen_at).toLocaleTimeString("vi-VN")}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
