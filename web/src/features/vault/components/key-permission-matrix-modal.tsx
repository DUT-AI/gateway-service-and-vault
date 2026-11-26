"use client";

import React, { useEffect, useState } from "react";
import {
  KeyRound,
  ShieldCheck,
  User,
  Users,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { NativeSelect } from "@/components/ui/native-select";
import {
  useGrantPermissionMutation,
  useIdentityPermissionsQuery,
  useRevokePermissionMutation,
} from "../hooks/use-permissions-queries";
import { useUserOptionsQuery } from "../hooks/use-user-options-query";

export interface KeyPermissionMatrixModalProps {
  projectId: string;
  projectName: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  availableKeys: string[];
}

export function KeyPermissionMatrixModal({
  projectId,
  projectName,
  open,
  onOpenChange,
  availableKeys,
}: KeyPermissionMatrixModalProps) {
  const [selectedUserId, setSelectedUserId] = useState<string>("");

  const { data: userOptions, isLoading: usersLoading } = useUserOptionsQuery();

  // Set default selected user
  useEffect(() => {
    if (userOptions && userOptions.length > 0 && !selectedUserId) {
      setSelectedUserId(String(userOptions[0].id));
    }
  }, [userOptions, selectedUserId]);

  const {
    data: permissionsData,
    isLoading: permissionsLoading,
  } = useIdentityPermissionsQuery(projectId, selectedUserId);

  const grantMutation = useGrantPermissionMutation(projectId);
  const revokeMutation = useRevokePermissionMutation(projectId);

  const permittedKeys = new Set(permissionsData?.permitted_keys ?? []);

  const handleToggle = async (key: string, isCurrentlyPermitted: boolean) => {
    if (!selectedUserId) return;

    try {
      if (isCurrentlyPermitted) {
        await revokeMutation.mutateAsync({
          identityId: selectedUserId,
          secretKey: key,
        });
        toast.success(`Đã thu hồi quyền đọc key ${key}`);
      } else {
        await grantMutation.mutateAsync({
          identity_id: selectedUserId,
          identity_type: "user",
          secret_key: key,
        });
        toast.success(`Đã cấp quyền đọc key ${key}`);
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Không thể cập nhật quyền");
    }
  };

  const selectedUser = userOptions?.find(
    (u) => String(u.id) === selectedUserId
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-base sm:text-lg font-bold text-slate-900">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
              <ShieldCheck className="h-4 w-4" />
            </div>
            Phân quyền đọc Secret Key
          </DialogTitle>
          <DialogDescription className="text-xs text-slate-500">
            Quản trị quyền truy cập cấp độ từng Key cho thành viên trong dự án{" "}
            <span className="font-semibold text-slate-700">{projectName}</span>.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {/* User Selector from Central Directory */}
          <div className="space-y-1.5">
            <label
              htmlFor="user-selector"
              className="text-xs font-semibold text-slate-700 flex items-center gap-1.5"
            >
              <Users className="h-3.5 w-3.5 text-slate-400" />
              Chọn người dùng (DUT-AI Directory)
            </label>

            {usersLoading ? (
              <Skeleton className="h-9 w-full rounded-md" />
            ) : (
              <NativeSelect
                id="user-selector"
                value={selectedUserId}
                onChange={(e) => setSelectedUserId(e.target.value)}
                className="font-medium text-slate-900 shadow-2xs"
              >
                {userOptions?.map((user) => (
                  <option key={user.id} value={String(user.id)}>
                    {user.name} ({user.email})
                  </option>
                ))}
              </NativeSelect>
            )}

            {selectedUser && (
              <div className="flex items-center gap-2 rounded-lg bg-slate-50 p-2 text-xs text-slate-600 border border-slate-200">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[#EEF3FA] text-[10px] font-bold text-[#042B5F]">
                  {selectedUser.name[0]?.toUpperCase() || "U"}
                </div>
                <span className="font-medium text-slate-800">
                  {selectedUser.name}
                </span>
                <span className="text-slate-400">({selectedUser.email})</span>
              </div>
            )}
          </div>

          {/* Key Permissions Checklist Matrix */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                <KeyRound className="h-3.5 w-3.5 text-slate-400" />
                Danh sách Secret Keys ({availableKeys.length})
              </label>
              <span className="text-[11px] text-slate-400">
                Tích chọn để cấp quyền đọc
              </span>
            </div>

            {permissionsLoading ? (
              <div className="space-y-2 border border-slate-200 rounded-lg p-3">
                <Skeleton className="h-6 w-full" />
                <Skeleton className="h-6 w-full" />
                <Skeleton className="h-6 w-full" />
              </div>
            ) : availableKeys.length === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-6 text-center text-xs text-slate-500">
                Dự án chưa có biến môi trường nào để phân quyền.
              </div>
            ) : (
              <div className="max-h-60 overflow-y-auto rounded-lg border border-slate-200 bg-white divide-y divide-slate-100">
                {availableKeys.map((key) => {
                  const isPermitted = permittedKeys.has(key);
                  const isPending =
                    grantMutation.isPending || revokeMutation.isPending;

                  return (
                    <div
                      key={key}
                      onClick={() => !isPending && handleToggle(key, isPermitted)}
                      className="flex items-center justify-between px-3 py-2.5 hover:bg-slate-50 cursor-pointer transition-colors"
                    >
                      <div className="flex items-center gap-2.5">
                        <Checkbox
                          checked={isPermitted}
                          disabled={isPending}
                          onCheckedChange={() => handleToggle(key, isPermitted)}
                        />
                        <span className="font-mono text-xs font-semibold text-slate-900">
                          {key}
                        </span>
                      </div>
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                          isPermitted
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                            : "bg-slate-100 text-slate-500"
                        }`}
                      >
                        {isPermitted ? "Được đọc" : "Chặn đọc"}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button
            type="button"
            onClick={() => onOpenChange(false)}
            className="w-full sm:w-auto bg-slate-900 text-white hover:bg-slate-800"
          >
            Đóng
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
