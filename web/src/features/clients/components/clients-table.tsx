"use client";

import React, { useMemo, useState } from "react";
import {
  AlertCircle,
  AlertTriangle,
  Ban,
  Calendar,
  Check,
  Container,
  Copy,
  Filter,
  HardDrive,
  Laptop,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  Server,
  Shield,
  ShieldAlert,
  ShieldCheck,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useAuth } from "@/contexts/auth-context";
import { useUserOptionsQuery } from "@/features/vault/hooks/use-user-options-query";
import { useClientsQuery, useRevokeClientMutation } from "../hooks/use-clients-queries";
import { RegisterClientDialog } from "./register-client-dialog";
import { CertDownloadDialog } from "./cert-download-dialog";
import { DockerDeploymentGuideDialog } from "./docker-deployment-guide-dialog";
import type { Client, ClientType, RegisterClientResult } from "../types";

export function ClientsTable() {
  const { user, isAdmin } = useAuth();
  const { data: clients, isLoading, error, refetch, isRefetching } =
    useClientsQuery();
  const { data: userOptions = [] } = useUserOptionsQuery();

  const [scopeTab, setScopeTab] = useState<"ALL" | "MINE">("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<"ALL" | ClientType>("ALL");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Dialog states
  const [registerOpen, setRegisterOpen] = useState(false);
  const [downloadOpen, setDownloadOpen] = useState(false);
  const [dockerGuideOpen, setDockerGuideOpen] = useState(false);
  const [downloadBundle, setDownloadBundle] =
    useState<RegisterClientResult | null>(null);
  const [clientToRevoke, setClientToRevoke] = useState<Client | null>(null);

  const revokeMutation = useRevokeClientMutation();

  const handleConfirmRevoke = async () => {
    if (!clientToRevoke) return;
    try {
      await revokeMutation.mutateAsync(clientToRevoke.id);
      toast.success(`Đã thu hồi thiết bị "${clientToRevoke.name}" thành công`);
      setClientToRevoke(null);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Không thể thu hồi thiết bị";
      toast.error(msg);
    }
  };

  const handleCopyFingerprint = async (clientId: string, fingerprint: string) => {
    try {
      await navigator.clipboard.writeText(fingerprint);
      setCopiedId(clientId);
      toast.success("Đã sao chép SHA-256 Fingerprint");
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      toast.error("Không thể sao chép fingerprint");
    }
  };

  const handleRegistrationSuccess = (result: RegisterClientResult) => {
    setDownloadBundle(result);
    setDownloadOpen(true);
  };

  const ownerMap = useMemo(() => {
    const map = new Map<string, (typeof userOptions)[number]>();
    userOptions.forEach((u) => map.set(String(u.id), u));
    return map;
  }, [userOptions]);

  // Filtering
  const filteredClients = useMemo(() => {
    if (!clients) return [];
    return clients.filter((client) => {
      // Admin scope filter
      if (isAdmin && scopeTab === "MINE" && user?.id) {
        if (client.owner_id !== String(user.id)) {
          return false;
        }
      }

      // Type filter
      if (typeFilter !== "ALL" && client.client_type !== typeFilter) {
        return false;
      }

      // Search filter (name, fingerprint, or owner name/email)
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase().trim();
      const owner = ownerMap.get(client.owner_id);
      const matchName = client.name.toLowerCase().includes(q);
      const matchFingerprint = client.cert_fingerprint.toLowerCase().includes(q);
      const matchOwner =
        owner?.name.toLowerCase().includes(q) ||
        owner?.email.toLowerCase().includes(q);
      return matchName || matchFingerprint || Boolean(matchOwner);
    });
  }, [clients, isAdmin, scopeTab, user?.id, typeFilter, searchQuery, ownerMap]);

  const getClientStatus = (client: Client) => {
    if (client.is_revoked) {
      return {
        label: "Đã thu hồi",
        variant: "destructive" as const,
        className: "bg-rose-50 text-rose-700 border-rose-200",
      };
    }

    const isExpired = new Date(client.expires_at).getTime() < Date.now();
    if (isExpired) {
      return {
        label: "Hết hạn",
        variant: "outline" as const,
        className: "bg-amber-50 text-amber-700 border-amber-200",
      };
    }

    return {
      label: "Đang hoạt động",
      variant: "outline" as const,
      className: "bg-emerald-50 text-emerald-700 border-emerald-200",
    };
  };

  return (
    <div className="space-y-4">
      {/* Admin Scope Tabs */}
      {isAdmin && (
        <div className="inline-flex items-center rounded-xl border border-slate-200 bg-slate-100 p-1">
          <button
            type="button"
            onClick={() => setScopeTab("ALL")}
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
            onClick={() => setScopeTab("MINE")}
            className={`cursor-pointer rounded-lg px-3.5 py-1.5 text-xs font-semibold transition-all ${
              scopeTab === "MINE"
                ? "bg-white text-blue-700 shadow-xs"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Thiết bị của tôi (
            {clients?.filter((c) => c.owner_id === String(user?.id)).length ?? 0}
            )
          </button>
        </div>
      )}

      {/* Top Filter and Actions Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Search input */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Tìm theo tên thiết bị hoặc fingerprint SHA-256..."
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

        {/* Type Filter and Register Action */}
        <div className="flex items-center gap-2">
          {/* Type Filter Pills */}
          <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs">
            <button
              type="button"
              onClick={() => setTypeFilter("ALL")}
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
              onClick={() => setTypeFilter("USER_DEVICE")}
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
              onClick={() => setTypeFilter("APP_SERVER")}
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
            variant="outline"
            size="sm"
            onClick={() => setDockerGuideOpen(true)}
            className="h-9 px-3 text-xs text-slate-700 border-slate-200 hover:bg-slate-50"
          >
            <Container className="h-3.5 w-3.5 mr-1.5 text-blue-600" />
            Hướng dẫn Docker Workload
          </Button>

          <Button
            type="button"
            size="sm"
            onClick={() => setRegisterOpen(true)}
            className="h-9 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-3 shadow-xs"
          >
            <Plus className="h-3.5 w-3.5 mr-1" />
            Đăng ký thiết bị mới
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
                  <th className="py-3 px-4">Tên thiết bị</th>
                  <th className="py-3 px-4">Chủ sở hữu</th>
                  <th className="py-3 px-4">Loại Client</th>
                  <th className="py-3 px-4">Fingerprint SHA-256</th>
                  <th className="py-3 px-4">Hạn chứng chỉ</th>
                  <th className="py-3 px-4 text-center">Trạng thái</th>
                  <th className="py-3 px-4 text-right">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {isLoading ? (
                  // Skeleton Loading Rows
                  Array.from({ length: 4 }).map((_, idx) => (
                    <tr key={idx} className="animate-pulse">
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2.5">
                          <Skeleton className="h-8 w-8 rounded-lg" />
                          <div className="space-y-1.5">
                            <Skeleton className="h-3.5 w-28" />
                            <Skeleton className="h-2.5 w-16" />
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <Skeleton className="h-5 w-24 rounded-full" />
                      </td>
                      <td className="py-3.5 px-4">
                        <Skeleton className="h-5 w-36 rounded-md" />
                      </td>
                      <td className="py-3.5 px-4">
                        <Skeleton className="h-3.5 w-20" />
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <Skeleton className="h-5 w-24 rounded-full mx-auto" />
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <Skeleton className="h-7 w-16 rounded-md ml-auto" />
                      </td>
                    </tr>
                  ))
                ) : error ? (
                  // Error State
                  <tr>
                    <td colSpan={7} className="py-8 text-center">
                      <div className="inline-flex flex-col items-center justify-center text-rose-600 gap-2">
                        <AlertCircle className="h-6 w-6" />
                        <span className="font-semibold">
                          Không thể tải danh sách thiết bị mTLS
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
                ) : filteredClients.length === 0 ? (
                  // Empty State
                  <tr>
                    <td colSpan={7} className="py-12 text-center">
                      <div className="flex flex-col items-center justify-center max-w-sm mx-auto text-center space-y-3">
                        <div className="h-12 w-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
                          <HardDrive className="h-6 w-6" />
                        </div>
                        <div>
                          <h4 className="text-sm font-semibold text-slate-900">
                            {searchQuery || typeFilter !== "ALL"
                              ? "Không tìm thấy thiết bị phù hợp"
                              : "Chưa có thiết bị mTLS nào"}
                          </h4>
                          <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                            {searchQuery || typeFilter !== "ALL"
                              ? "Hãy thử thay đổi từ khóa tìm kiếm hoặc bộ lọc loại thiết bị."
                              : "Đăng ký máy tính cá nhân (Developer PC) hoặc máy chủ (Server) để cấp chứng chỉ mTLS truy cập Zero-Trust Gateway."}
                          </p>
                        </div>
                        {searchQuery || typeFilter !== "ALL" ? (
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSearchQuery("");
                              setTypeFilter("ALL");
                            }}
                            className="text-xs"
                          >
                            Xóa bộ lọc
                          </Button>
                        ) : (
                          <Button
                            type="button"
                            size="sm"
                            onClick={() => setRegisterOpen(true)}
                            className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium"
                          >
                            <Plus className="h-3.5 w-3.5 mr-1" />
                            Đăng ký thiết bị đầu tiên
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ) : (
                  // Client Rows
                  filteredClients.map((client) => {
                    const status = getClientStatus(client);
                    const isDeveloper = client.client_type === "USER_DEVICE";
                    const owner = ownerMap.get(client.owner_id);

                    return (
                      <tr
                        key={client.id}
                        className="hover:bg-slate-50/70 transition-colors"
                      >
                        {/* Device Name */}
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2.5">
                            <div
                              className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 ${
                                isDeveloper
                                  ? "bg-blue-50 text-blue-600"
                                  : "bg-purple-50 text-purple-600"
                              }`}
                            >
                              {isDeveloper ? (
                                <Laptop className="h-4 w-4" />
                              ) : (
                                <Server className="h-4 w-4" />
                              )}
                            </div>
                            <div className="truncate max-w-[200px] sm:max-w-xs">
                              <div className="font-semibold text-slate-900 truncate">
                                {client.name}
                              </div>
                              <div className="text-[10px] text-slate-400 font-mono">
                                SN: {client.cert_serial.slice(0, 12)}...
                              </div>
                            </div>
                          </div>
                        </td>

                        {/* Owner */}
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2 min-w-0">
                            {owner?.avatar_url ? (
                              <img
                                src={owner.avatar_url}
                                alt={owner.name}
                                className="h-6 w-6 rounded-full object-cover border border-slate-200 shrink-0"
                              />
                            ) : (
                              <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-[10px] font-bold text-slate-600">
                                {(owner?.name || client.owner_id || "U")[0].toUpperCase()}
                              </div>
                            )}
                            <div className="min-w-0 max-w-[160px]">
                              <div className="font-medium text-slate-800 truncate">
                                {owner?.name || `User #${client.owner_id}`}
                              </div>
                              {owner?.email && (
                                <div className="text-[10px] text-slate-400 truncate">
                                  {owner.email}
                                </div>
                              )}
                            </div>
                          </div>
                        </td>

                        {/* Client Type */}
                        <td className="py-3 px-4">
                          <Badge
                            variant="outline"
                            className={`text-[10px] font-semibold border ${
                              isDeveloper
                                ? "bg-blue-50 text-blue-700 border-blue-200"
                                : "bg-purple-50 text-purple-700 border-purple-200"
                            }`}
                          >
                            {isDeveloper ? "Developer PC" : "Workload Server"}
                          </Badge>
                        </td>

                        {/* Fingerprint SHA-256 */}
                        <td className="py-3 px-4">
                          <div className="inline-flex items-center gap-1.5 bg-slate-100/80 px-2 py-1 rounded-md border border-slate-200 font-mono text-[11px] text-slate-700">
                            <span className="truncate max-w-[140px] sm:max-w-[180px]">
                              {client.cert_fingerprint.slice(0, 16)}...
                              {client.cert_fingerprint.slice(-8)}
                            </span>
                            <button
                              type="button"
                              onClick={() =>
                                handleCopyFingerprint(
                                  client.id,
                                  client.cert_fingerprint
                                )
                              }
                              className="text-slate-400 hover:text-slate-700 transition-colors p-0.5"
                              title="Sao chép toàn bộ Fingerprint"
                            >
                              {copiedId === client.id ? (
                                <Check className="h-3 w-3 text-emerald-600" />
                              ) : (
                                <Copy className="h-3 w-3" />
                              )}
                            </button>
                          </div>
                        </td>

                        {/* Expiration Date */}
                        <td className="py-3 px-4 text-slate-600">
                          <div className="flex items-center gap-1.5">
                            <Calendar className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                            <span>
                              {new Date(client.expires_at).toLocaleDateString(
                                "vi-VN"
                              )}
                            </span>
                          </div>
                        </td>

                        {/* Status */}
                        <td className="py-3 px-4 text-center">
                          <Badge
                            variant={status.variant}
                            className={`text-[10px] font-semibold border ${status.className}`}
                          >
                            {status.label}
                          </Badge>
                        </td>

                        {/* Actions */}
                        <td className="py-3 px-4 text-right">
                          {client.is_revoked ? (
                            <span className="text-[11px] text-slate-400 font-medium">
                              Đã thu hồi
                            </span>
                          ) : (
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => setClientToRevoke(client)}
                              className="h-7 text-xs text-rose-600 hover:text-rose-700 hover:bg-rose-50 px-2"
                              title="Thu hồi thiết bị và tất cả Virtual Keys liên kết"
                            >
                              <Ban className="h-3 w-3 mr-1" />
                              Thu hồi
                            </Button>
                          )}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Revocation Confirmation Dialog */}
      <Dialog
        open={!!clientToRevoke}
        onOpenChange={(open) => !open && setClientToRevoke(null)}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <div className="flex items-center gap-2 text-rose-600 mb-1">
              <AlertTriangle className="h-5 w-5" />
              <DialogTitle>Xác nhận thu hồi thiết bị mTLS</DialogTitle>
            </div>
            <DialogDescription className="text-xs text-slate-500">
              Hành động này sẽ vô hiệu hóa vĩnh viễn thiết bị phần cứng này và lập
              tức thu hồi toàn bộ Virtual Access Keys đang hoạt động liên kết với
              thiết bị này.
            </DialogDescription>
          </DialogHeader>

          {clientToRevoke && (
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5 my-2">
              <div className="flex justify-between">
                <span className="text-slate-500">Thiết bị:</span>
                <span className="font-semibold text-slate-900">
                  {clientToRevoke.name}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Fingerprint:</span>
                <span className="font-mono text-slate-700">
                  {clientToRevoke.cert_fingerprint.slice(0, 16)}...
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Loại:</span>
                <span className="font-medium text-slate-800">
                  {clientToRevoke.client_type === "USER_DEVICE"
                    ? "Developer PC"
                    : "Workload Server"}
                </span>
              </div>
            </div>
          )}

          <DialogFooter className="pt-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setClientToRevoke(null)}
              disabled={revokeMutation.isPending}
              className="text-xs"
            >
              Hủy
            </Button>
            <Button
              type="button"
              size="sm"
              onClick={handleConfirmRevoke}
              disabled={revokeMutation.isPending}
              className="bg-rose-600 hover:bg-rose-700 text-white text-xs font-medium"
            >
              {revokeMutation.isPending ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" />
                  Đang thu hồi...
                </>
              ) : (
                <>
                  <Ban className="h-3.5 w-3.5 mr-1" />
                  Xác nhận thu hồi ngay
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialogs */}
      <RegisterClientDialog
        open={registerOpen}
        onOpenChange={setRegisterOpen}
        onSuccess={handleRegistrationSuccess}
      />

      <CertDownloadDialog
        open={downloadOpen}
        onOpenChange={setDownloadOpen}
        bundle={downloadBundle}
      />

      <DockerDeploymentGuideDialog
        open={dockerGuideOpen}
        onOpenChange={setDockerGuideOpen}
      />
    </div>
  );
}
