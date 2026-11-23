"use client";

import React, { useMemo, useState } from "react";
import {
  AlertCircle,
  AlertTriangle,
  Ban,
  Calendar,
  Check,
  HardDrive,
  Key,
  Laptop,
  Loader2,
  RefreshCw,
  Server,
  Shield,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
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
import { useClientsQuery, type Client } from "@/features/clients";
import {
  useProjectKeysQuery,
  useRevokeKeyMutation,
} from "../hooks/use-keys-queries";
import type { VirtualKey } from "../types";

export interface VirtualKeysTableProps {
  projectId: string;
  onGenerateClick?: () => void;
}

export function VirtualKeysTable({
  projectId,
  onGenerateClick,
}: VirtualKeysTableProps) {
  const {
    data: keys,
    isLoading: keysLoading,
    error: keysError,
    refetch,
    isRefetching,
  } = useProjectKeysQuery(projectId);

  const { data: clients } = useClientsQuery();
  const revokeMutation = useRevokeKeyMutation(projectId);

  // Client lookup map for instant device info display
  const clientsMap = useMemo(() => {
    const map = new Map<string, Client>();
    if (clients) {
      for (const client of clients) {
        map.set(client.id, client);
      }
    }
    return map;
  }, [clients]);

  // Revocation Confirmation State
  const [keyToRevoke, setKeyToRevoke] = useState<VirtualKey | null>(null);

  const handleConfirmRevoke = async () => {
    if (!keyToRevoke) return;

    try {
      await revokeMutation.mutateAsync(keyToRevoke.id);
      toast.success(
        `Đã thu hồi Virtual Key (${keyToRevoke.key_prefix}...) thành công`
      );
      setKeyToRevoke(null);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Đã xảy ra lỗi khi thu hồi Virtual Key";
      toast.error(msg);
    }
  };

  return (
    <div className="space-y-4">
      {/* Table Card */}
      <Card className="border-slate-200 bg-white overflow-hidden shadow-xs">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-600 font-semibold">
                <tr>
                  <th className="py-3 px-4">Key Prefix</th>
                  <th className="py-3 px-4">Thiết bị ràng buộc (Client)</th>
                  <th className="py-3 px-4">Thời điểm cấp</th>
                  <th className="py-3 px-4 text-center">Trạng thái</th>
                  <th className="py-3 px-4 text-right">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {keysLoading ? (
                  // Skeleton Loading Rows
                  Array.from({ length: 3 }).map((_, idx) => (
                    <tr key={idx} className="animate-pulse">
                      <td className="py-3.5 px-4">
                        <Skeleton className="h-5 w-28 rounded-md" />
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <Skeleton className="h-6 w-6 rounded-md" />
                          <Skeleton className="h-4 w-32" />
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <Skeleton className="h-3.5 w-24" />
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <Skeleton className="h-5 w-20 rounded-full mx-auto" />
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <Skeleton className="h-7 w-16 rounded-md ml-auto" />
                      </td>
                    </tr>
                  ))
                ) : keysError ? (
                  // Error State
                  <tr>
                    <td colSpan={5} className="py-8 text-center">
                      <div className="inline-flex flex-col items-center justify-center text-rose-600 gap-2">
                        <AlertCircle className="h-6 w-6" />
                        <span className="font-semibold">
                          Không thể tải danh sách Virtual Keys
                        </span>
                        <p className="text-slate-500 text-xs max-w-sm">
                          {keysError.message}
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
                ) : !keys || keys.length === 0 ? (
                  // Empty State
                  <tr>
                    <td colSpan={5} className="py-12 text-center">
                      <div className="flex flex-col items-center justify-center max-w-sm mx-auto text-center space-y-3">
                        <div className="h-12 w-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                          <Key className="h-6 w-6" />
                        </div>
                        <div>
                          <h4 className="text-sm font-semibold text-slate-900">
                            Chưa có Virtual Key nào
                          </h4>
                          <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                            Khóa ảo Virtual Key ràng buộc 1:1 với chứng chỉ mTLS
                            của thiết bị phần cứng để bảo vệ kết nối API Gateway.
                          </p>
                        </div>
                        {onGenerateClick && (
                          <Button
                            type="button"
                            size="sm"
                            onClick={onGenerateClick}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium"
                          >
                            <Key className="h-3.5 w-3.5 mr-1" />
                            Cấp Virtual Key đầu tiên
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ) : (
                  // Key Rows
                  keys.map((key) => {
                    const isRevoked = key.status === "REVOKED";
                    const boundClient = clientsMap.get(key.client_id);
                    const isDev =
                      !boundClient || boundClient.client_type === "USER_DEVICE";

                    return (
                      <tr
                        key={key.id}
                        className="hover:bg-slate-50/70 transition-colors"
                      >
                        {/* Key Prefix */}
                        <td className="py-3 px-4">
                          <div className="inline-flex items-center gap-1.5 bg-slate-100/90 px-2.5 py-1 rounded-md border border-slate-200 font-mono text-[11px] font-semibold text-slate-800">
                            <Key className="h-3 w-3 text-slate-500 shrink-0" />
                            <span>{key.key_prefix}...</span>
                          </div>
                        </td>

                        {/* Bound Client Device */}
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <div
                              className={`h-6 w-6 rounded-md flex items-center justify-center shrink-0 ${
                                isDev
                                  ? "bg-blue-50 text-blue-600"
                                  : "bg-purple-50 text-purple-600"
                              }`}
                            >
                              {isDev ? (
                                <Laptop className="h-3.5 w-3.5" />
                              ) : (
                                <Server className="h-3.5 w-3.5" />
                              )}
                            </div>
                            <div className="truncate max-w-[180px]">
                              <span className="font-semibold text-slate-800 truncate block">
                                {boundClient?.name ?? (
                                  <span className="font-mono text-slate-400">
                                    {key.client_id.slice(0, 10)}...
                                  </span>
                                )}
                              </span>
                              {boundClient?.is_revoked && (
                                <span className="text-[10px] text-rose-600 font-medium">
                                  (Thiết bị đã thu hồi)
                                </span>
                              )}
                            </div>
                          </div>
                        </td>

                        {/* Created At */}
                        <td className="py-3 px-4 text-slate-600">
                          <div className="flex items-center gap-1.5">
                            <Calendar className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                            <span>
                              {new Date(key.created_at).toLocaleString("vi-VN")}
                            </span>
                          </div>
                        </td>

                        {/* Status */}
                        <td className="py-3 px-4 text-center">
                          <Badge
                            variant={isRevoked ? "destructive" : "outline"}
                            className={`text-[10px] font-semibold border ${
                              isRevoked
                                ? "bg-rose-50 text-rose-700 border-rose-200"
                                : "bg-emerald-50 text-emerald-700 border-emerald-200"
                            }`}
                          >
                            {isRevoked ? "Đã thu hồi" : "Đang hoạt động"}
                          </Badge>
                        </td>

                        {/* Action: Revoke */}
                        <td className="py-3 px-4 text-right">
                          {isRevoked ? (
                            <span className="text-[11px] text-slate-400 italic">
                              Đã thu hồi
                            </span>
                          ) : (
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => setKeyToRevoke(key)}
                              className="h-7 px-2.5 text-xs text-rose-700 border-rose-200 hover:bg-rose-50 hover:text-rose-800"
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
        open={Boolean(keyToRevoke)}
        onOpenChange={(open) => !open && setKeyToRevoke(null)}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <div className="flex items-center gap-2.5">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-100 text-rose-700">
                <ShieldAlert className="h-5 w-5" />
              </div>
              <div>
                <DialogTitle className="text-base font-semibold text-slate-900">
                  Xác nhận thu hồi Virtual Key
                </DialogTitle>
                <DialogDescription className="text-xs text-slate-500">
                  Thao tác này sẽ ngắt kết nối ngay lập tức tại Gateway.
                </DialogDescription>
              </div>
            </div>
          </DialogHeader>

          {keyToRevoke && (
            <div className="space-y-3 pt-1 text-xs">
              <div className="rounded-xl border border-rose-200 bg-rose-50/80 p-3.5 space-y-1.5 text-rose-950">
                <p className="font-semibold flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4 text-rose-600 shrink-0" />
                  Cảnh báo: Hành động không thể hoàn tác!
                </p>
                <p className="text-[11px] text-rose-800 leading-relaxed">
                  Ngay sau khi xác nhận, toàn bộ ứng dụng và script đang sử dụng
                  Virtual Key với prefix{" "}
                  <strong className="font-mono">{keyToRevoke.key_prefix}...</strong>{" "}
                  sẽ bị APISIX Gateway từ chối kết nối với mã lỗi{" "}
                  <code className="font-mono bg-rose-100 px-1 py-0.5 rounded">
                    HTTP 403 Forbidden
                  </code>
                  .
                </p>
              </div>

              <div className="rounded-lg border border-slate-200 p-3 bg-slate-50/60 space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-500">Mã Key Prefix:</span>
                  <span className="font-mono font-semibold text-slate-800">
                    {keyToRevoke.key_prefix}...
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Thiết bị ràng buộc:</span>
                  <span className="font-semibold text-slate-800">
                    {clientsMap.get(keyToRevoke.client_id)?.name ??
                      keyToRevoke.client_id.slice(0, 12)}
                  </span>
                </div>
              </div>
            </div>
          )}

          <DialogFooter className="pt-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setKeyToRevoke(null)}
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
    </div>
  );
}
