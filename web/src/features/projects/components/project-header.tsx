"use client";

import React, { useState } from "react";
import { Calendar, Check, Copy, FolderKanban, Shield } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Project } from "../types";

export interface ProjectHeaderProps {
  project: Project;
}

export function ProjectHeader({ project }: ProjectHeaderProps) {
  const [copied, setCopied] = useState(false);

  const formattedDate = new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "full",
  }).format(new Date(project.created_at));

  const handleCopySlug = async () => {
    try {
      await navigator.clipboard.writeText(project.slug);
      setCopied(true);
      toast.success("Đã sao chép slug vào clipboard!");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Không thể sao chép");
    }
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-1.5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#EEF3FA] text-[#042B5F]">
              <FolderKanban className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
                {project.name}
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-2 pt-1">
            <Badge
              variant="outline"
              className="font-mono text-xs bg-slate-50 text-slate-700 border-slate-200"
            >
              #{project.slug}
            </Badge>
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={handleCopySlug}
              title="Sao chép slug"
              className="text-slate-400 hover:text-slate-700 h-6 w-6"
            >
              {copied ? (
                <Check className="h-3.5 w-3.5 text-emerald-600" />
              ) : (
                <Copy className="h-3.5 w-3.5" />
              )}
            </Button>
            <span className="text-slate-300">|</span>
            <span className="flex items-center gap-1.5 text-xs text-slate-500">
              <Calendar className="h-3.5 w-3.5 text-slate-400" />
              Khởi tạo: {formattedDate}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge
            variant="secondary"
            className="bg-emerald-50 text-emerald-800 border-emerald-200 text-xs font-semibold px-2.5 py-1"
          >
            <Shield className="h-3 w-3 mr-1 text-emerald-600" />
            Đang hoạt động
          </Badge>
        </div>
      </div>

      <div className="border-t border-slate-100 pt-3">
        <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
          {project.description ||
            "Không gian làm việc cho dự án này chưa có mô tả chi tiết."}
        </p>
      </div>
    </div>
  );
}
