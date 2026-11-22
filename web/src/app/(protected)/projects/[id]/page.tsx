"use client";

import React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AlertCircle, ArrowLeft, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { useProjectDetailQuery } from "@/features/projects/hooks/use-projects-queries";
import { ProjectHeader } from "@/features/projects/components/project-header";
import { ProjectWorkspaceTabs } from "@/features/projects/components/project-workspace-tabs";

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const projectId = params?.id ?? "";

  const {
    data: project,
    isLoading,
    error,
    refetch,
    isRefetching,
  } = useProjectDetailQuery(projectId);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-5 w-48" />
        <div className="rounded-xl border border-slate-200 bg-white p-6 space-y-4">
          <div className="flex items-center gap-3">
            <Skeleton className="h-10 w-10 rounded-xl" />
            <div className="space-y-2 flex-1">
              <Skeleton className="h-6 w-1/3" />
              <Skeleton className="h-4 w-1/4" />
            </div>
          </div>
          <Skeleton className="h-12 w-full" />
        </div>
        <Skeleton className="h-10 w-80 rounded-xl" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="space-y-6">
        <Breadcrumbs
          items={[
            { label: "Dự án", href: "/projects" },
            { label: "Chi tiết dự án" },
          ]}
        />
        <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center max-w-md mx-auto space-y-4 shadow-xs">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-50 text-rose-600">
            <AlertCircle className="h-7 w-7" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">
            Không tìm thấy dự án
          </h2>
          <p className="text-xs text-slate-500 leading-relaxed">
            Dự án có mã định danh{" "}
            <span className="font-mono text-slate-700 font-medium">
              {projectId}
            </span>{" "}
            không tồn tại hoặc bạn không có quyền truy cập.
          </p>
          <div className="flex justify-center gap-3 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetch()}
              disabled={isRefetching}
            >
              <RefreshCw
                className={`h-3.5 w-3.5 mr-1.5 ${
                  isRefetching ? "animate-spin" : ""
                }`}
              />
              Thử lại
            </Button>
            <Button
              size="sm"
              asChild
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Link href="/projects">
                <ArrowLeft className="h-3.5 w-3.5 mr-1.5" />
                Về danh sách dự án
              </Link>
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Breadcrumbs
        items={[
          { label: "Dự án", href: "/projects" },
          { label: project.name },
        ]}
      />

      <ProjectHeader project={project} />

      <ProjectWorkspaceTabs project={project} />
    </div>
  );
}
