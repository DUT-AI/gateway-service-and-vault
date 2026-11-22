"use client";

import { LoginForm } from "@/features/auth";
import { redirectToSsoLogin } from "@/lib/auth-urls";
import { Sparkles } from "lucide-react";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-sm rounded-xl border border-gray-200 bg-white p-6 shadow-md">
        <div className="mb-6 text-center">
          <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm">
            <Sparkles className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">
            Đăng nhập hệ thống
          </h1>
          <p className="mt-1 text-xs text-gray-500">
            Hệ sinh thái DUT AI Platform
          </p>
        </div>

        {/* Central SSO Login Button */}
        <button
          type="button"
          onClick={() => redirectToSsoLogin()}
          className="shadow-xs mb-5 flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
        >
          <Sparkles className="h-4 w-4" />
          Đăng nhập bằng DUT-AI Workspace (SSO)
        </button>

        <div className="relative mb-4 flex items-center py-2">
          <div className="flex-grow border-t border-gray-200"></div>
          <span className="mx-3 flex-shrink text-xs font-medium uppercase text-gray-400">
            Hoặc tài khoản nội bộ
          </span>
          <div className="flex-grow border-t border-gray-200"></div>
        </div>

        <LoginForm />
      </div>
    </main>
  );
}
