"use client";

import React, { useMemo, useState } from "react";
import {
  AlertCircle,
  Check,
  Clock,
  Copy,
  ExternalLink,
  Globe,
  Plus,
  RefreshCw,
  Search,
  Server,
  Shield,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { useServicesQuery } from "../hooks/use-services-queries";
import { CreateServiceDialog } from "./create-service-dialog";
import type { AuthType, UpstreamService } from "../types";

export function ServicesTable() {
  const { data: services, isLoading, error, refetch, isRefetching } =
    useServicesQuery();

  const [searchQuery, setSearchQuery] = useState("");
  const [authFilter, setAuthFilter] = useState<"ALL" | AuthType>("ALL");
  const [copiedUrlId, setCopiedUrlId] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const handleCopyUrl = async (id: string, url: string) => {
    try {
      await navigator.clipboard.writeText(url);
      setCopiedUrlId(id);
      toast.success("Đã sao chép Base URL vào bộ nhớ tạm");
      setTimeout(() => setCopiedUrlId(null), 2000);
    } catch {
      toast.error("Không thể sao chép URL");
    }
  };

  const filteredServices = useMemo(() => {
    if (!services) return [];
    return services.filter((svc) => {
      // Auth Type Filter
      if (authFilter !== "ALL" && svc.auth_type !== authFilter) {
        return false;
      }

      // Search Filter
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase().trim();
      const matchName = svc.name.toLowerCase().includes(q);
      const matchSlug = svc.slug.toLowerCase().includes(q);
      const matchUrl = svc.base_url.toLowerCase().includes(q);
      return matchName || matchSlug || matchUrl;
    });
  }, [services, authFilter, searchQuery]);

  const renderAuthBadge = (authType: string) => {
    switch (authType) {
      case "BEARER_TOKEN":
        return (
          <Badge
            variant="outline"
            className="text-[10px] font-semibold bg-blue-50 text-blue-700 border-blue-200"
          >
            Bearer Token
          </Badge>
        );
      case "API_KEY":
        return (
          <Badge
            variant="outline"
            className="text-[10px] font-semibold bg-purple-50 text-purple-700 border-purple-200"
          >
            API Key
          </Badge>
        );
      case "BASIC_AUTH":
        return (
          <Badge
            variant="outline"
            className="text-[10px] font-semibold bg-amber-50 text-amber-700 border-amber-200"
          >
            Basic Auth
          </Badge>
        );
      case "NO_AUTH":
      default:
        return (
          <Badge
            variant="outline"
            className="text-[10px] font-semibold bg-slate-50 text-slate-700 border-slate-200"
          >
            No Auth
          </Badge>
        );
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Filter and Actions Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Search input */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Tìm theo tên dịch vụ, slug hoặc URL đích..."
            className="pl-9 pr-8 text-xs h-9 bg-white border-slate-200"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        {/* Filter Pills and Action Button */}
        <div className="flex items-center gap-2">
          {/* Auth filter pills */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs">
            <button
              type="button"
              onClick={() => setAuthFilter("ALL")}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                authFilter === "ALL"
                  ? "bg-white text-slate-800 shadow-xs"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              Tất cả
            </button>
            <button
              type="button"
              onClick={() => setAuthFilter("BEARER_TOKEN")}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                authFilter === "BEARER_TOKEN"
                  ? "bg-white text-blue-700 shadow-xs"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              Bearer
            </button>
            <button
              type="button"
              onClick={() => setAuthFilter("API_KEY")}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                authFilter === "API_KEY"
                  ? "bg-white text-purple-700 shadow-xs"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              API Key
            </button>
          </div>

          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => refetch()}
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
            size="sm"
            onClick={() => setCreateDialogOpen(true)}
            className="h-9 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-3 shadow-xs"
          >
            <Plus className="h-3.5 w-3.5 mr-1" />
            Khai báo dịch vụ mới
          </Button>
        </div>
      </div>

      {/* Main Table Card */}
      <Card className="border-slate-200 bg-white overflow-hidden shadow-xs">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold">
                <tr>
                  <th className="py-3 px-4">Tên dịch vụ & Slug</th>
                  <th className="py-3 px-4">Base URL (Endpoint)</th>
                  <th className="py-3 px-4">Phương thức xác thực</th>
                  <th className="py-3 px-4">Timeout</th>
                  <th className="py-3 px-4 text-center">Trạng thái</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {isLoading ? (
                  // Skeleton Loading
                  Array.from({ length: 3 }).map((_, idx) => (
                    <tr key={idx} className="animate-pulse">
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2.5">
                          <Skeleton className="h-8 w-8 rounded-lg" />
                          <div className="space-y-1.5">
                            <Skeleton className="h-3.5 w-32" />
                            <Skeleton className="h-2.5 w-20" />
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <Skeleton className="h-4 w-48" />
                      </td>
                      <td className="py-3.5 px-4">
                        <Skeleton className="h-5 w-24 rounded-full" />
                      </td>
                      <td className="py-3.5 px-4">
                        <Skeleton className="h-3.5 w-12" />
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <Skeleton className="h-5 w-24 rounded-full mx-auto" />
                      </td>
                    </tr>
                  ))
                ) : error ? (
                  // Error State
                  <tr>
                    <td colSpan={5} className="py-8 text-center">
                      <div className="inline-flex flex-col items-center justify-center text-rose-600 gap-2">
                        <AlertCircle className="h-6 w-6" />
                        <span className="font-semibold">
                          Không thể tải danh sách dịch vụ Upstream
                        </span>
                        <p className="text-slate-500 text-xs max-w-sm">
                          {error.message}
                        </p>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => refetch()}
                          className="mt-2 text-xs"
                        >
                          Thử lại
                        </Button>
                      </div>
                    </td>
                  </tr>
                ) : filteredServices.length === 0 ? (
                  // Empty State
                  <tr>
                    <td colSpan={5} className="py-12 text-center">
                      <div className="flex flex-col items-center justify-center max-w-sm mx-auto text-center space-y-3">
                        <div className="h-12 w-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
                          <Globe className="h-6 w-6" />
                        </div>
                        <div>
                          <h4 className="text-sm font-semibold text-slate-900">
                            {searchQuery || authFilter !== "ALL"
                              ? "Không tìm thấy dịch vụ phù hợp"
                              : "Chưa có dịch vụ Upstream nào"}
                          </h4>
                          <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                            {searchQuery || authFilter !== "ALL"
                              ? "Hãy thử tìm kiếm với từ khóa khác hoặc bỏ lọc phương thức xác thực."
                              : "Khai báo dịch vụ đối tác (OpenAI, Payment API,...) để Gateway tự động tiêm bảo mật và chuyển tiếp request an toàn."}
                          </p>
                        </div>
                        {searchQuery || authFilter !== "ALL" ? (
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSearchQuery("");
                              setAuthFilter("ALL");
                            }}
                            className="text-xs"
                          >
                            Xóa bộ lọc
                          </Button>
                        ) : (
                          <Button
                            type="button"
                            size="sm"
                            onClick={() => setCreateDialogOpen(true)}
                            className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium"
                          >
                            <Plus className="h-3.5 w-3.5 mr-1" />
                            Khai báo dịch vụ đầu tiên
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ) : (
                  // Services Rows
                  filteredServices.map((svc) => (
                    <tr
                      key={svc.id}
                      className="hover:bg-slate-50/70 transition-colors"
                    >
                      {/* Name & Slug */}
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2.5">
                          <div className="h-8 w-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                            <Globe className="h-4 w-4" />
                          </div>
                          <div className="truncate max-w-[200px] sm:max-w-xs">
                            <div className="font-semibold text-slate-900 truncate">
                              {svc.name}
                            </div>
                            <div className="inline-block mt-0.5">
                              <Badge
                                variant="outline"
                                className="text-[10px] font-mono bg-slate-50 text-slate-600 px-1.5 py-0 border-slate-200"
                              >
                                {svc.slug}
                              </Badge>
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Base URL */}
                      <td className="py-3 px-4 font-mono text-[11px] text-slate-700">
                        <div className="inline-flex items-center gap-1.5 bg-slate-50 px-2 py-1 rounded-md border border-slate-200 max-w-[240px] sm:max-w-sm truncate">
                          <span className="truncate">{svc.base_url}</span>
                          <button
                            type="button"
                            onClick={() => handleCopyUrl(svc.id, svc.base_url)}
                            className="text-slate-400 hover:text-slate-700 transition-colors shrink-0"
                            title="Sao chép Base URL"
                          >
                            {copiedUrlId === svc.id ? (
                              <Check className="h-3 w-3 text-emerald-600" />
                            ) : (
                              <Copy className="h-3 w-3" />
                            )}
                          </button>
                        </div>
                      </td>

                      {/* Auth Type */}
                      <td className="py-3 px-4">
                        {renderAuthBadge(svc.auth_type)}
                      </td>

                      {/* Timeout */}
                      <td className="py-3 px-4 text-slate-600">
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3 text-slate-400" />
                          <span>{svc.timeout_seconds}s</span>
                        </div>
                      </td>

                      {/* Status */}
                      <td className="py-3 px-4 text-center">
                        <Badge
                          variant={svc.is_active ? "outline" : "destructive"}
                          className={`text-[10px] font-semibold border ${
                            svc.is_active
                              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                              : "bg-rose-50 text-rose-700 border-rose-200"
                          }`}
                        >
                          {svc.is_active ? "Đang hoạt động" : "Tạm dừng"}
                        </Badge>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Create Service Modal */}
      <CreateServiceDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />
    </div>
  );
}
