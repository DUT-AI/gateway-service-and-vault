"use client";

import { LoginForm } from "@/features/auth";
import { Sparkles } from "lucide-react";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-50 via-gray-50 to-blue-50/30 p-4">
      <div className="w-full max-w-md rounded-2xl border border-gray-200/80 bg-white/95 p-8 shadow-xl shadow-gray-200/50 backdrop-blur-sm">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20">
            <Sparkles className="h-6 w-6" />
          </div>

          <h1 className="text-2xl font-bold tracking-tight text-gray-900">
            Cổng đăng nhập SSO
          </h1>
          <p className="mt-1 text-xs text-gray-500">
            Hệ thống Secure API Gateway & Dynamic Vault
          </p>
        </div>

        <LoginForm />
      </div>

      <p className="mt-6 text-center text-xs text-gray-400">
        Bảo mật Zero-Trust • Quản lý danh tính tập trung bởi DUT-AI
      </p>
    </main>
  );
}
