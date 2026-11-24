import Link from "next/link";
import { ArrowLeft, Info, ShieldAlert } from "lucide-react";

export default function RegisterPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-50 via-gray-50 to-blue-50/30 p-4">
      <div className="w-full max-w-md rounded-2xl border border-gray-200/80 bg-white/95 p-8 text-center shadow-xl shadow-gray-200/50 backdrop-blur-sm">
        <div className="mx-auto mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100 text-amber-600">
          <ShieldAlert className="h-6 w-6" />
        </div>
        <h1 className="text-xl font-bold text-gray-900">
          Đăng ký tài khoản tập trung
        </h1>
        <p className="mt-2 text-sm text-gray-600 leading-relaxed">
          Hệ thống hiện tại hoạt động theo mô hình <strong>Pure SSO</strong>. Toàn
          bộ tài khoản và phân quyền người dùng được quản lý trực tiếp bởi hệ
          thống <strong>DUT-AI Manage</strong>.
        </p>

        <div className="my-6 rounded-lg border border-blue-100 bg-blue-50/80 p-3.5 text-left text-xs text-blue-900">
          <div className="flex items-start gap-2">
            <Info className="mt-0.5 h-4 w-4 shrink-0 text-blue-600" />
            <p>
              Để đăng ký tài khoản mới hoặc yêu cầu cấp quyền truy cập vào Gateway
              & Vault, vui lòng liên hệ quản trị viên tổ chức của bạn.
            </p>
          </div>
        </div>

        <Link
          href="/login"
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-blue-500/25 transition-all hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Quay lại trang Đăng nhập SSO</span>
        </Link>
      </div>
    </main>
  );
}
