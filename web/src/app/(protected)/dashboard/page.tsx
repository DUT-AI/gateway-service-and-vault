"use client";

import { useAuth } from "@/contexts/auth-context";
import { Sparkles, User, Mail, Shield, Key } from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();

  const displayRole =
    user?.role_names && user.role_names.length > 0
      ? user.role_names.join(", ")
      : (user?.role ?? "Thành viên");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Tổng quan tài khoản
        </h1>
        <p className="text-sm text-slate-500">
          Chào mừng{" "}
          <span className="font-medium text-slate-800">
            {user?.name || user?.email}
          </span>{" "}
          quay trở lại DUT AI Platform.
        </p>
      </div>

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
                ? new Date(user.created_at).toLocaleString()
                : "Đã xác thực SSO"}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-slate-500">
              Hệ sinh thái DUT-AI
            </dt>
            <dd className="mt-1 flex items-center gap-1.5 text-sm font-medium text-emerald-600">
              <Sparkles className="h-4 w-4" /> Đã kết nối True SSO & App
              Launcher
            </dd>
          </div>
        </dl>

        {user?.permissions && user.permissions.length > 0 && (
          <div className="mt-5 border-t border-slate-100 pt-4">
            <h3 className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-slate-700">
              <Key className="h-3.5 w-3.5 text-slate-500" /> Danh sách quyền hạn
              (Permissions)
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {user.permissions.map((perm) => (
                <span
                  key={perm}
                  className="inline-flex items-center rounded border border-slate-200 bg-slate-100 px-2 py-0.5 font-mono text-[11px] text-slate-700"
                >
                  {perm}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
