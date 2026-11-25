"use client";

import React, { useMemo, useState } from "react";
import { AlertCircle, HardDrive, Plus } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/contexts/auth-context";
import { useUserOptionsQuery } from "@/features/vault/hooks/use-user-options-query";
import {
  useClientsQuery,
  useRevokeClientMutation,
} from "../hooks/use-clients-queries";
import { ClientsToolbar } from "./clients-toolbar";
import { ClientRow } from "./client-row";
import { RevokeClientDialog } from "./revoke-client-dialog";
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

  const filteredClients = useMemo(() => {
    if (!clients) return [];
    return clients.filter((client) => {
      if (isAdmin && scopeTab === "MINE" && user?.id) {
        if (client.owner_id !== String(user.id)) return false;
      }
      if (typeFilter !== "ALL" && client.client_type !== typeFilter) {
        return false;
      }
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase().trim();
      const owner = ownerMap.get(client.owner_id);
      return (
        client.name.toLowerCase().includes(q) ||
        client.cert_fingerprint.toLowerCase().includes(q) ||
        Boolean(owner?.name.toLowerCase().includes(q)) ||
        Boolean(owner?.email.toLowerCase().includes(q))
      );
    });
  }, [clients, isAdmin, scopeTab, user, typeFilter, searchQuery, ownerMap]);

  return (
    <div className="space-y-4">
      <ClientsToolbar
        isAdmin={isAdmin}
        clients={clients}
        currentUserId={user?.id}
        scopeTab={scopeTab}
        onScopeTabChange={setScopeTab}
        searchQuery={searchQuery}
        onSearchQueryChange={setSearchQuery}
        typeFilter={typeFilter}
        onTypeFilterChange={setTypeFilter}
        isRefetching={isRefetching}
        onRefresh={() => refetch()}
        onOpenDockerGuide={() => setDockerGuideOpen(true)}
        onOpenRegister={() => setRegisterOpen(true)}
      />

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
                        <Skeleton className="h-5 w-20 rounded-full" />
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
                  filteredClients.map((client) => (
                    <ClientRow
                      key={client.id}
                      client={client}
                      owner={ownerMap.get(client.owner_id)}
                      isCopied={copiedId === client.id}
                      onCopyFingerprint={handleCopyFingerprint}
                      onRevokeClick={setClientToRevoke}
                    />
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <RevokeClientDialog
        client={clientToRevoke}
        isPending={revokeMutation.isPending}
        onClose={() => setClientToRevoke(null)}
        onConfirm={handleConfirmRevoke}
      />

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
