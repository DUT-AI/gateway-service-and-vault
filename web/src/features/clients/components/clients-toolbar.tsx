"use client";

import React from "react";
import { Container, Laptop, Plus, RefreshCw, Search, Server, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { Client, ClientType } from "../types";

export interface ClientsToolbarProps {
  isAdmin: boolean;
  clients?: Client[];
  currentUserId?: string | number;
  scopeTab: "ALL" | "MINE";
  onScopeTabChange: (tab: "ALL" | "MINE") => void;
  searchQuery: string;
  onSearchQueryChange: (value: string) => void;
  typeFilter: "ALL" | ClientType;
  onTypeFilterChange: (type: "ALL" | ClientType) => void;
  isRefetching: boolean;
  onRefresh: () => void;
  onOpenDockerGuide: () => void;
  onOpenRegister: () => void;
}

export function ClientsToolbar({
  isAdmin,
  clients,
  currentUserId,
  scopeTab,
  onScopeTabChange,
  searchQuery,
  onSearchQueryChange,
  typeFilter,
  onTypeFilterChange,
  isRefetching,
  onRefresh,
  onOpenDockerGuide,
  onOpenRegister,
}: ClientsToolbarProps) {
  const myClientsCount =
    clients?.filter((c) => c.owner_id === String(currentUserId)).length ?? 0;

  return (
    <div className="space-y-4">
      {isAdmin && (
        <div className="inline-flex items-center rounded-xl border border-slate-200 bg-slate-100 p-1">
          <button
            type="button"
            onClick={() => onScopeTabChange("ALL")}
            className={`cursor-pointer rounded-lg px-3.5 py-1.5 text-xs font-semibold transition-all ${
              scopeTab === "ALL"
                ? "bg-white text-blue-700 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Tất cả hệ thống ({clients?.length ?? 0})
          </button>
          <button
            type="button"
            onClick={() => onScopeTabChange("MINE")}
            className={`cursor-pointer rounded-lg px-3.5 py-1.5 text-xs font-semibold transition-all ${
              scopeTab === "MINE"
                ? "bg-white text-blue-700 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Thiết bị của tôi ({myClientsCount})
          </button>
        </div>
      )}

      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
          <Input
            value={searchQuery}
            onChange={(e) => onSearchQueryChange(e.target.value)}
            placeholder="Tìm theo tên thiết bị hoặc fingerprint SHA-256..."
            className="pl-9 pr-8 text-xs h-9 bg-white border-slate-200"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => onSearchQueryChange("")}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs">
            <button
              type="button"
              onClick={() => onTypeFilterChange("ALL")}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                typeFilter === "ALL"
                  ? "bg-white text-slate-800 shadow-xs"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              Tất cả
            </button>
            <button
              type="button"
              onClick={() => onTypeFilterChange("USER_DEVICE")}
              className={`px-2.5 py-1 rounded-md font-medium transition-all flex items-center gap-1 ${
                typeFilter === "USER_DEVICE"
                  ? "bg-white text-blue-700 shadow-xs"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              <Laptop className="h-3 w-3" />
              Dev PC
            </button>
            <button
              type="button"
              onClick={() => onTypeFilterChange("APP_SERVER")}
              className={`px-2.5 py-1 rounded-md font-medium transition-all flex items-center gap-1 ${
                typeFilter === "APP_SERVER"
                  ? "bg-white text-purple-700 shadow-xs"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              <Server className="h-3 w-3" />
              Server
            </button>
          </div>

          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onRefresh}
            disabled={isRefetching}
            className="h-9 px-2.5 text-xs text-slate-600 border-slate-200"
            title="Làm mới danh sách"
          >
            <RefreshCw
              className={`h-3.5 w-3.5 ${isRefetching ? "animate-spin" : ""}`}
            />
          </Button>

          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onOpenDockerGuide}
            className="h-9 px-3 text-xs text-slate-700 border-slate-200 hover:bg-slate-50"
          >
            <Container className="h-3.5 w-3.5 mr-1.5 text-blue-600" />
            Hướng dẫn Docker Workload
          </Button>

          <Button
            type="button"
            size="sm"
            onClick={onOpenRegister}
            className="h-9 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-3 shadow-xs"
          >
            <Plus className="h-3.5 w-3.5 mr-1" />
            Đăng ký thiết bị mới
          </Button>
        </div>
      </div>
    </div>
  );
}
