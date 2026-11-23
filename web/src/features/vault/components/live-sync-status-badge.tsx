"use client";

import React from "react";
import { Loader2, Radio, RefreshCw, Wifi, WifiOff } from "lucide-react";
import type { SseConnectionStatus } from "../types/stream-types";

export interface LiveSyncStatusBadgeProps {
  status: SseConnectionStatus;
  lastPing: Date | null;
  onReconnect?: () => void;
  className?: string;
}

export function LiveSyncStatusBadge({
  status,
  lastPing,
  onReconnect,
  className = "",
}: LiveSyncStatusBadgeProps) {
  const formattedPing = lastPing
    ? new Intl.DateTimeFormat("vi-VN", {
        timeStyle: "medium",
      }).format(lastPing)
    : null;

  if (status === "connected") {
    return (
      <div
        className={`inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50/90 px-2.5 py-1 text-xs font-semibold text-emerald-800 shadow-2xs transition-all ${className}`}
        title={`Đang kết nối luồng SSE trực tiếp${
          formattedPing ? ` (Heartbeat: ${formattedPing})` : ""
        }`}
      >
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
        </span>
        <span className="flex items-center gap-1">
          <Radio className="h-3 w-3 text-emerald-600" />
          Live Sync
        </span>
      </div>
    );
  }

  if (status === "connecting") {
    return (
      <div
        className={`inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-800 shadow-2xs ${className}`}
        title="Đang tái kết nối tới máy chủ SSE..."
      >
        <Loader2 className="h-3 w-3 animate-spin text-amber-600" />
        <span>Đang kết nối lại...</span>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={onReconnect}
      className={`inline-flex cursor-pointer items-center gap-1.5 rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600 transition-colors hover:bg-slate-200 ${className}`}
      title="Mất kết nối với luồng SSE. Bấm để thử lại."
    >
      <WifiOff className="h-3 w-3 text-slate-500" />
      <span>Ngoại tuyến</span>
      <RefreshCw className="h-2.5 w-2.5 ml-0.5 text-slate-400" />
    </button>
  );
}
