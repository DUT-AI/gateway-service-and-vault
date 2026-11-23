"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FolderKanban,
  KeyRound,
  Server,
  LogOut,
  Menu,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import { useAuth } from "@/contexts/auth-context";
import { DutaiWaffle } from "@/components/common/DutaiWaffle";

interface NavItemConfig {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  match: (pathname: string) => boolean;
}

const NAV_ITEMS: NavItemConfig[] = [
  {
    href: "/dashboard",
    label: "Dashboard",
    icon: LayoutDashboard,
    match: (pathname: string) => pathname === "/dashboard",
  },
  {
    href: "/projects",
    label: "Dự án",
    icon: FolderKanban,
    match: (pathname: string) =>
      pathname === "/projects" || pathname.startsWith("/projects/"),
  },
  {
    href: "/clients",
    label: "Thiết bị & Client",
    icon: KeyRound,
    match: (pathname: string) => pathname.startsWith("/clients"),
  },
  {
    href: "/services",
    label: "Dịch vụ hệ thống",
    icon: Server,
    match: (pathname: string) => pathname.startsWith("/services"),
  },
  {
    href: "/audit",
    label: "Nhật ký an ninh",
    icon: ShieldAlert,
    match: (pathname: string) => pathname.startsWith("/audit"),
  },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const getPageHeaderTitle = () => {
    if (pathname === "/dashboard") return "Dashboard";
    if (pathname.startsWith("/projects")) return "Dự án & Không gian làm việc";
    if (pathname.startsWith("/clients")) return "Thiết bị & Client";
    if (pathname.startsWith("/services")) return "Dịch vụ hệ thống";
    if (pathname.startsWith("/audit")) return "Nhật ký an ninh & Cảnh báo";
    return "Không gian làm việc";
  };

  const sidebarContent = (
    <>
      <div className="flex h-16 items-center gap-3 border-b border-slate-200 px-5">
        <div className="shadow-xs flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-white">
          <Sparkles className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <span className="block truncate text-sm font-bold text-slate-900">
            DUT AI Platform
          </span>
          <p className="text-[11px] text-slate-500">Gateway & Vault</p>
        </div>
        <button
          type="button"
          aria-label="Đóng menu"
          className="ml-auto inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 md:hidden"
          onClick={() => setMobileOpen(false)}
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <nav
        aria-label="Điều hướng chính"
        className="flex-1 space-y-1 overflow-y-auto p-3"
      >
        <p className="px-3 pb-2 pt-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
          Không gian làm việc
        </p>
        {NAV_ITEMS.map((item) => {
          const isActive = item.match(pathname);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className={`flex min-h-[44px] items-center justify-between rounded-lg border px-3 text-xs font-semibold transition-colors duration-150 ${isActive
                  ? "border-blue-200 bg-blue-50 text-blue-800"
                  : "border-transparent text-slate-600 hover:bg-slate-50 hover:text-slate-950"
                }`}
            >
              <span className="flex items-center gap-2.5">
                <Icon
                  className={`h-4 w-4 ${isActive ? "text-blue-600" : "text-slate-400"
                    }`}
                />
                {item.label}
              </span>
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-slate-200 p-3">
        <div className="flex items-center gap-2.5 rounded-lg border border-slate-200 bg-white p-2">
          {user?.avatar_url ? (
            <img
              src={user.avatar_url}
              className="h-8 w-8 rounded-full object-cover"
            />
          ) : (
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
              {(user?.name || user?.email || "U")[0].toUpperCase()}
            </div>
          )}
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-semibold text-slate-900">
              {user?.name || user?.email || "Người dùng"}
            </p>
            <p className="truncate text-[10px] uppercase text-slate-500">
              {user?.role || "Thành viên"}
            </p>
          </div>
          <button
            type="button"
            aria-label="Đăng xuất"
            onClick={() => logout()}
            className="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-md text-slate-400 transition-colors hover:bg-rose-50 hover:text-rose-600"
            title="Đăng xuất"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </>
  );

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 antialiased">
      {/* Desktop Persistent Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col border-r border-slate-200 bg-white md:flex">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-50 bg-slate-950/40 md:hidden"
          onClick={() => setMobileOpen(false)}
        >
          <aside
            className="flex h-full w-[min(86vw,300px)] flex-col bg-white shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {sidebarContent}
          </aside>
        </div>
      )}

      {/* Main Content Area */}
      <div className="min-w-0 md:ml-64">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur sm:px-6 lg:px-8">
          <div className="flex min-w-0 items-center gap-2 text-xs text-slate-500">
            <button
              type="button"
              onClick={() => setMobileOpen(true)}
              aria-label="Mở menu"
              className="inline-flex h-9 w-9 cursor-pointer items-center justify-center rounded-lg text-slate-600 hover:bg-slate-100 md:hidden"
            >
              <Menu className="h-5 w-5" />
            </button>
            <span className="text-sm font-semibold text-slate-800">
              {getPageHeaderTitle()}
            </span>
          </div>

          <div className="flex items-center gap-3">

            {/* DUT-AI Ecosystem Waffle Launcher */}
            <div className="flex items-center border-l border-slate-200 pl-3">
              <DutaiWaffle current="data" />
            </div>

            <button
              type="button"
              onClick={() => logout()}
              className="inline-flex cursor-pointer items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
            >
              <LogOut className="h-3.5 w-3.5 text-slate-500" />
              <span className="hidden sm:inline">Đăng xuất</span>
            </button>
          </div>
        </header>

        <main className="mx-auto max-w-7xl p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
