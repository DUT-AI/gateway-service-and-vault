"use client";

import React, { useState } from "react";
import {
  Activity,
  Check,
  Clock,
  Pause,
  Play,
  RotateCcw,
  Sparkles,
  Trash2,
  User,
  X,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { SseSecretUpdateEvent } from "../types/stream-types";

export interface LiveAuditFeedProps {
  events: SseSecretUpdateEvent[];
  isPaused: boolean;
  onTogglePause: () => void;
  onClearHistory: () => void;
}

export function LiveAuditFeed({
  events,
  isPaused,
  onTogglePause,
  onClearHistory,
}: LiveAuditFeedProps) {
  const [open, setOpen] = useState(false);

  const formatRelativeTime = (timestamp: string) => {
    try {
      const now = Date.now();
      const eventTime = new Date(timestamp).getTime();
      const diffSec = Math.floor((now - eventTime) / 1000);

      if (diffSec < 5) return "vừa xong";
      if (diffSec < 60) return `${diffSec} giây trước`;
      const diffMin = Math.floor(diffSec / 60);
      if (diffMin < 60) return `${diffMin} phút trước`;
      return new Date(timestamp).toLocaleTimeString("vi-VN");
    } catch {
      return timestamp;
    }
  };

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setOpen(true)}
        className="border-slate-200 text-slate-700 hover:bg-slate-50"
      >
        <Activity className="h-3.5 w-3.5 mr-1.5 text-[#042B5F]" />
        <span>Nhật ký Live</span>
        {events.length > 0 && (
          <Badge
            variant="secondary"
            className="ml-1.5 h-4.5 px-1.5 bg-[#EEF3FA] text-[#042B5F] text-[10px]"
          >
            {events.length}
          </Badge>
        )}
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <div className="flex items-center justify-between pr-4">
              <DialogTitle className="flex items-center gap-2 text-base font-bold text-slate-900">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#EEF3FA] text-[#042B5F]">
                  <Activity className="h-4 w-4" />
                </div>
                Nhật ký sự kiện Live Stream
              </DialogTitle>
            </div>
            <DialogDescription className="text-xs text-slate-500">
              Các sự kiện cập nhật cấu hình được truyền phát tức thì qua Redis
              Pub/Sub & SSE.
            </DialogDescription>
          </DialogHeader>

          {/* Action Toolbar */}
          <div className="flex items-center justify-between border-y border-slate-100 py-2 text-xs">
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={onTogglePause}
                className="h-7 text-xs text-slate-600 hover:text-slate-900"
              >
                {isPaused ? (
                  <>
                    <Play className="h-3.5 w-3.5 mr-1 text-emerald-600" />
                    Tiếp tục stream
                  </>
                ) : (
                  <>
                    <Pause className="h-3.5 w-3.5 mr-1 text-amber-600" />
                    Tạm dừng
                  </>
                )}
              </Button>
            </div>

            {events.length > 0 && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={onClearHistory}
                className="h-7 text-xs text-rose-600 hover:bg-rose-50 hover:text-rose-700"
              >
                <Trash2 className="h-3.5 w-3.5 mr-1" />
                Xóa lịch sử
              </Button>
            )}
          </div>

          {/* Events List */}
          <div className="max-h-72 overflow-y-auto space-y-2.5 py-1">
            {events.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500 space-y-1">
                <p className="font-semibold text-slate-700">
                  Chưa có sự kiện thay đổi nào
                </p>
                <p className="text-[11px] text-slate-400">
                  Khi bất kỳ ai thêm hoặc sửa biến môi trường, thông báo sẽ
                  xuất hiện tại đây ngay lập tức.
                </p>
              </div>
            ) : (
              events.map((evt) => (
                <div
                  key={evt.event_id}
                  className="rounded-lg border border-slate-200 bg-slate-50/70 p-3 space-y-1.5 transition-all hover:bg-white hover:shadow-2xs"
                >
                  <div className="flex items-center justify-between text-[11px]">
                    <div className="flex items-center gap-1.5 text-slate-600">
                      <User className="h-3 w-3 text-slate-400" />
                      <span className="font-semibold text-slate-800">
                        {evt.actor || "Hệ thống"}
                      </span>
                    </div>
                    <span className="flex items-center gap-1 text-[10px] text-slate-400">
                      <Clock className="h-3 w-3" />
                      {formatRelativeTime(evt.timestamp)}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 flex-wrap pt-0.5">
                    <span className="text-xs text-slate-700">
                      Đã cập nhật biến:
                    </span>
                    {evt.changed_keys?.map((key) => (
                      <Badge
                        key={key}
                        variant="secondary"
                        className="font-mono text-[11px] bg-[#EEF3FA] text-[#042B5F] border border-[#042B5F]/20"
                      >
                        {key}
                      </Badge>
                    ))}
                    <Badge
                      variant="outline"
                      className="font-mono text-[10px] text-slate-500"
                    >
                      Scope: {evt.scope_name}
                    </Badge>
                    <span className="text-[10px] text-slate-400 ml-auto">
                      v{evt.new_version}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
