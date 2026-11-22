import Link from "next/link";
import { Button } from "@/components/ui/button";
import { DutaiWaffle } from "@/components/common/DutaiWaffle";
import { Sparkles } from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top Navbar */}
      <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-6 backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="shadow-xs flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-white">
            <Sparkles className="h-5 w-5" />
          </div>
          <span className="text-base font-bold text-slate-900">
            Project Boilerplate
          </span>
        </div>

        <div className="flex items-center gap-4">
          {/* DUT-AI Ecosystem Waffle Menu */}
          <div className="flex items-center border-r border-slate-200 pr-4">
            <DutaiWaffle current="data" />
          </div>

          <Button variant="secondary" asChild>
            <Link href="/login">Đăng nhập</Link>
          </Button>
          <Button asChild>
            <Link href="/dashboard">Dashboard</Link>
          </Button>
        </div>
      </header>

      <main className="mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-5xl flex-col justify-center px-6 py-16">
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-600">
          Next.js Modular Boilerplate
        </p>
        <h1 className="mt-4 max-w-3xl text-5xl font-bold leading-tight text-slate-950">
          Hệ thống Boilerplate theo chuẩn DUT AI Data Platform.
        </h1>
        <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">
          Kiến trúc Clean Architecture, Dishka DI, Transactional Outbox, chuẩn
          hóa phân trang và tích hợp Menu 9-chấm DUT-AI Workspace.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button asChild>
            <Link href="/dashboard">Vào Dashboard</Link>
          </Button>
          <Button variant="secondary" asChild>
            <Link href="/login">Đăng nhập</Link>
          </Button>
        </div>
      </main>
    </div>
  );
}
