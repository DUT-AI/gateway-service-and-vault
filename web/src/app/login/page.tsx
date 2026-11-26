"use client";

import { LoginForm } from "@/features/auth";
import { ShieldCheck } from "lucide-react";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-[#F6F8FC] p-4">
      <div className="w-full max-w-md rounded-2xl border border-slate-200/90 bg-white p-8 shadow-sm">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3.5 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-[#042B5F] text-white shadow-xs">
            <ShieldCheck className="h-6 w-6" />
          </div>

          <h1 className="text-xl font-bold tracking-tight text-[#042B5F]">
            Cổng đăng nhập SSO
          </h1>
          <p className="mt-1 text-xs text-slate-500">
            Hệ thống DUT-AI Secure API Gateway &amp; Dynamic Vault
          </p>
        </div>

        <LoginForm />
      </div>

      <p className="mt-6 text-center text-xs text-slate-400">
        Bảo mật Zero-Trust &bull; Quản lý danh tính tập trung bởi DUT-AI
      </p>
    </main>
  );
}
