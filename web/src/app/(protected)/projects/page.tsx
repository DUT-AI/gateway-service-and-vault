"use client";

import React, { useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/auth-context";
import { useProjectsQuery } from "@/features/projects/hooks/use-projects-queries";
import { ProjectList } from "@/features/projects/components/project-list";
import { CreateProjectDialog } from "@/features/projects/components/create-project-dialog";

export default function ProjectsPage() {
  const { isAdmin } = useAuth();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const {
    data: projects,
    isLoading,
    error,
    refetch,
    isRefetching,
  } = useProjectsQuery();

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Quản lý Dự án
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Không gian làm việc cho các dịch vụ ứng dụng, cấu hình bảo mật Vault
            và phân quyền Virtual Keys.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isLoading || isRefetching}
            className="text-slate-600 border-slate-200"
          >
            <RefreshCw
              className={`h-3.5 w-3.5 mr-1.5 ${
                isRefetching ? "animate-spin" : ""
              }`}
            />
            Làm mới
          </Button>
          {isAdmin && (
            <Button
              size="sm"
              onClick={() => setCreateDialogOpen(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium shadow-xs"
            >
              <Plus className="h-4 w-4 mr-1.5" />
              Tạo dự án mới
            </Button>
          )}
        </div>
      </div>

      <ProjectList
        projects={projects}
        isLoading={isLoading}
        error={error}
        onRetry={() => refetch()}
        onCreateProject={isAdmin ? () => setCreateDialogOpen(true) : undefined}
      />

      {isAdmin && (
        <CreateProjectDialog
          open={createDialogOpen}
          onOpenChange={setCreateDialogOpen}
        />
      )}
    </div>
  );
}
