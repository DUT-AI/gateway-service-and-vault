"use client";

import { LoginForm } from "@/features/auth";
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

        <LoginForm />
      </div>
    </main>
  );
}
