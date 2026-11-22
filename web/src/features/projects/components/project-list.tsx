"use client";

import React from "react";
import { FolderKanban, FolderPlus, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ProjectCard } from "./project-card";
import type { Project } from "../types";

export interface ProjectListProps {
  projects?: Project[];
  isLoading: boolean;
  error?: Error | null;
  onRetry?: () => void;
  onCreateProject?: () => void;
}

export function ProjectList({
  projects,
  isLoading,
  error,
  onRetry,
  onCreateProject,
}: ProjectListProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <div
            key={index}
            className="rounded-xl border border-slate-200 bg-white p-5 space-y-4"
          >
            <div className="flex items-center gap-3">
              <Skeleton className="h-8 w-8 rounded-lg" />
              <div className="space-y-1.5 flex-1">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/3" />
              </div>
            </div>
            <Skeleton className="h-10 w-full" />
            <div className="pt-2 border-t border-slate-100 flex justify-between items-center">
              <Skeleton className="h-3 w-24" />
              <Skeleton className="h-3 w-16" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-rose-200 bg-rose-50/50 p-6 text-center space-y-3">
        <p className="text-sm font-semibold text-rose-800">
          Không thể tải danh sách dự án
        </p>
        <p className="text-xs text-rose-600">
          {error.message || "Đã xảy ra lỗi khi kết nối tới máy chủ Gateway."}
        </p>
        {onRetry && (
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            className="border-rose-200 bg-white hover:bg-rose-50 text-rose-700"
          >
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
            Thử lại
          </Button>
        )}
      </div>
    );
  }

  if (!projects || projects.length === 0) {
    return (
      <div className="rounded-2xl border-2 border-dashed border-slate-200 bg-white p-10 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 mb-4">
          <FolderPlus className="h-7 w-7" />
        </div>
        <h3 className="text-base font-semibold text-slate-900">
          Chưa có dự án nào
        </h3>
        <p className="mt-1.5 text-xs text-slate-500 max-w-sm mx-auto leading-relaxed">
          Tạo không gian làm việc dự án đầu tiên để cấu hình biến môi trường
          Vault và chính sách bảo mật Virtual Keys.
        </p>
        {onCreateProject && (
          <div className="mt-6">
            <Button
              onClick={onCreateProject}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium shadow-xs"
            >
              <FolderPlus className="h-4 w-4 mr-1.5" />
              Tạo dự án mới
            </Button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {projects.map((project) => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  );
}
