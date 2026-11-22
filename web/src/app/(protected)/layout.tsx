"use client";

import { useEffect } from "react";
import { useAuth } from "@/contexts/auth-context";
import { AppShell } from "@/components/layout/app-shell";
import { redirectToSsoLogin } from "@/lib/auth-urls";
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading, error, refetchUser } = useAuth();

  useEffect(() => {
    // Chỉ redirect sang login khi không có lỗi server bận và không có user
    if (!isLoading && !error && !user) {
      redirectToSsoLogin();
    }
  }, [user, isLoading, error]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-slate-950">
        <div className="flex flex-col items-center gap-3">
          <div className="border-3 h-8 w-8 animate-spin rounded-full border-blue-600 border-t-transparent" />
          <p className="text-xs font-medium text-slate-500">
            Đang xác thực tài khoản DUT AI SSO...
          </p>
        </div>
      </div>
    );
  }

  // Nếu máy chủ xác thực bận hoặc gặp lỗi kết nối -> hiển thị thông báo lỗi, không tự ý fake user
  if (error && !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4 dark:bg-slate-950">
        <div className="w-full max-w-md space-y-4 rounded-xl border border-rose-200 bg-white p-6 text-center shadow-sm dark:border-rose-900/40 dark:bg-slate-900">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-600">
            <AlertTriangle className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
              Máy chủ xác thực đang bận
            </h2>
            <p className="mt-1 text-xs leading-relaxed text-slate-500">
              {error.message ||
                "Không thể kết nối đến máy chủ xác thực Manage IdP. Vui lòng kiểm tra lại kết nối mạng hoặc thử lại sau."}
            </p>
          </div>
          <div className="flex justify-center gap-3 pt-2">
            <button
              onClick={() => refetchUser()}
              className="inline-flex cursor-pointer items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white transition-colors hover:bg-blue-700"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Thử lại
            </button>
            <button
              onClick={() => redirectToSsoLogin()}
              className="cursor-pointer rounded-lg border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-50"
            >
              Về trang đăng nhập
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return <AppShell>{children}</AppShell>;
}
