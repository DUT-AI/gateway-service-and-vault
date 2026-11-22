"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/auth-context";
import {
  Sparkles,
  User,
  Mail,
  Shield,
  FolderKanban,
  ArrowRight,
  Plus,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useProjectsQuery } from "@/features/projects/hooks/use-projects-queries";
import { CreateProjectDialog } from "@/features/projects/components/create-project-dialog";

export default function DashboardPage() {
  const { user } = useAuth();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const { data: projects, isLoading: projectsLoading } = useProjectsQuery();

  const displayRole =
    user?.role_names && user.role_names.length > 0
      ? user.role_names.join(", ")
      : (user?.role ?? "Thành viên");

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Tổng quan tài khoản
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Chào mừng{" "}
            <span className="font-medium text-slate-800">
              {user?.name || user?.email}
            </span>{" "}
            quay trở lại DUT AI Platform.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            onClick={() => setCreateDialogOpen(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium shadow-xs"
          >
            <Plus className="h-4 w-4 mr-1.5" />
            Tạo dự án mới
          </Button>
          <Button size="sm" variant="outline" asChild className="border-slate-200">
            <Link href="/projects">
              <FolderKanban className="h-4 w-4 mr-1.5 text-blue-600" />
              Tất cả dự án
            </Link>
          </Button>
        </div>
      </div>

      {/* User Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="shadow-xs rounded-xl border border-slate-200 bg-white p-5">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-50 p-2 text-blue-600">
              <User className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-slate-500">Họ và tên</p>
              <p className="text-sm font-semibold text-slate-900">
                {user?.name ?? "Chưa thiết lập"}
              </p>
            </div>
          </div>
        </div>

        <div className="shadow-xs rounded-xl border border-slate-200 bg-white p-5">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600">
              <Mail className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-slate-500">Địa chỉ Email</p>
              <p className="text-sm font-semibold text-slate-900">
                {user?.email}
              </p>
            </div>
          </div>
        </div>

        <div className="shadow-xs rounded-xl border border-slate-200 bg-white p-5">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-purple-50 p-2 text-purple-600">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-slate-500">Vai trò / Phân quyền</p>
              <p className="text-sm font-semibold text-slate-900">
                <span className="uppercase">{displayRole}</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Projects Workspace Hub Card */}
      <div className="shadow-xs rounded-xl border border-slate-200 bg-white p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
              <FolderKanban className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">
                Không gian dự án
              </h2>
              <p className="text-xs text-slate-500">
                Quản lý các workspace và cấu hình bảo mật API
              </p>
            </div>
          </div>
          <Link
            href="/projects"
            className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700"
          >
            Xem tất cả
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {projectsLoading ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 pt-2">
            <Skeleton className="h-24 w-full rounded-xl" />
            <Skeleton className="h-24 w-full rounded-xl" />
            <Skeleton className="h-24 w-full rounded-xl" />
          </div>
        ) : !projects || projects.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/50 p-6 text-center">
            <p className="text-xs text-slate-500">
              Bạn chưa có dự án nào trong hệ thống.
            </p>
            <Button
              size="sm"
              variant="outline"
              onClick={() => setCreateDialogOpen(true)}
              className="mt-3 text-xs text-blue-600 border-blue-200 hover:bg-blue-50"
            >
              <Plus className="h-3.5 w-3.5 mr-1" />
              Khởi tạo dự án đầu tiên
            </Button>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 pt-2">
            {projects.slice(0, 3).map((proj) => (
              <Link
                key={proj.id}
                href={`/projects/${proj.id}`}
                className="group block rounded-xl border border-slate-200 p-4 transition-all hover:border-blue-200 hover:bg-blue-50/20 hover:shadow-xs"
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-900 group-hover:text-blue-600 truncate">
                    {proj.name}
                  </h3>
                  <Badge variant="secondary" className="font-mono text-[10px]">
                    #{proj.slug}
                  </Badge>
                </div>
                <p className="mt-1.5 text-xs text-slate-500 line-clamp-2">
                  {proj.description || "Không có mô tả chi tiết."}
                </p>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* SSO Profile Details */}
      <div className="shadow-xs rounded-xl border border-slate-200 bg-white p-6">
        <h2 className="mb-4 text-base font-semibold text-slate-900">
          Chi tiết hồ sơ định danh DUT-AI SSO
        </h2>
        <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
          <div>
            <dt className="text-xs font-medium text-slate-500">
              Mã định danh (User ID)
            </dt>
            <dd className="mt-1 text-sm font-medium text-slate-900">
              {user?.id}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-slate-500">
              Ảnh đại diện (Avatar URL)
            </dt>
            <dd className="mt-1 text-sm font-medium text-slate-900">
              {user?.avatar_url ?? "Mặc định"}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-slate-500">
              Ngày tham gia
            </dt>
            <dd className="mt-1 text-sm font-medium text-slate-900">
              {user?.created_at
                ? new Date(user.created_at).toLocaleString("vi-VN")
                : "Không có dữ liệu"}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-slate-500">
              Trạng thái tài khoản
            </dt>
            <dd className="mt-1 flex items-center gap-1.5 text-sm font-semibold text-emerald-700">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              Đang hoạt động (Active)
            </dd>
          </div>
        </dl>
      </div>

      <CreateProjectDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />
    </div>
  );
}
