"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Check,
  ChevronDown,
  Loader2,
  Search,
  Trash2,
  UserPlus,
  Users,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useUserOptionsQuery } from "@/features/vault/hooks/use-user-options-query";
import {
  useAddProjectMemberMutation,
  useProjectMembersQuery,
  useRemoveProjectMemberMutation,
} from "../hooks/use-member-queries";

export interface ProjectMembersViewProps {
  projectId: string;
  projectName: string;
}

export function ProjectMembersView({
  projectId,
  projectName,
}: ProjectMembersViewProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [selectedUserIds, setSelectedUserIds] = useState<number[]>([]);
  const [isSubmittingBatch, setIsSubmittingBatch] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const { data: userOptions = [], isLoading: usersLoading } =
    useUserOptionsQuery();
  const { data: members = [], isLoading: membersLoading } =
    useProjectMembersQuery(projectId, true);

  const addMutation = useAddProjectMemberMutation(projectId);
  const removeMutation = useRemoveProjectMemberMutation(projectId);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const memberUserIds = useMemo(
    () => new Set(members.map((m) => m.user_id)),
    [members]
  );

  const availableUsers = useMemo(
    () => userOptions.filter((u) => !memberUserIds.has(u.id)),
    [userOptions, memberUserIds]
  );

  const filteredAvailableUsers = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return availableUsers;
    return availableUsers.filter(
      (u) =>
        u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    );
  }, [availableUsers, searchQuery]);

  const userMap = useMemo(() => {
    const map = new Map<number, (typeof userOptions)[number]>();
    userOptions.forEach((u) => map.set(u.id, u));
    return map;
  }, [userOptions]);

  const selectedSet = useMemo(() => new Set(selectedUserIds), [selectedUserIds]);

  const toggleUserSelection = (userId: number) => {
    setSelectedUserIds((prev) =>
      prev.includes(userId)
        ? prev.filter((id) => id !== userId)
        : [...prev, userId]
    );
  };

  const handleAddSelected = async () => {
    if (selectedUserIds.length === 0) return;
    setIsSubmittingBatch(true);
    try {
      await addMutation.mutateAsync({ user_ids: selectedUserIds });
      toast.success(
        `Đã thêm ${selectedUserIds.length} thành viên vào dự án!`
      );
      setSelectedUserIds([]);
      setSearchQuery("");
      setDropdownOpen(false);
    } catch (err: any) {
      toast.error(
        err?.response?.data?.detail || "Không thể thêm thành viên vào dự án"
      );
    } finally {
      setIsSubmittingBatch(false);
    }
  };

  const handleRemove = async (userId: number) => {
    try {
      await removeMutation.mutateAsync(userId);
      toast.success("Đã xóa thành viên khỏi dự án!");
    } catch (err: any) {
      toast.error(
        err?.response?.data?.detail || "Không thể xóa thành viên khỏi dự án"
      );
    }
  };

  return (
    <Card className="min-h-[600px] border-slate-200 bg-white shadow-2xs">
      <CardHeader className="border-b border-slate-100 pb-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle className="text-base font-semibold text-slate-900 flex items-center gap-2">
              <Users className="h-4 w-4 text-blue-600" />
              Quản lý thành viên dự án
            </CardTitle>
            <p className="text-xs text-slate-500 mt-1">
              Tìm kiếm và chỉ định nhiều người dùng từ DUT-AI SSO được phép truy
              cập vào dự án{" "}
              <span className="font-semibold text-slate-700">
                {projectName}
              </span>
              .
            </p>
          </div>
          <Badge
            variant="secondary"
            className="bg-slate-100 text-slate-700 text-xs font-semibold w-fit"
          >
            {members.length} thành viên
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-5 pt-5">
        {/* Searchable Multi-Select Combobox */}
        <div className="space-y-3 max-w-2xl" ref={containerRef}>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
              <Input
                value={searchQuery}
                onFocus={() => setDropdownOpen(true)}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setDropdownOpen(true);
                }}
                placeholder={
                  usersLoading
                    ? "Đang tải danh sách người dùng..."
                    : availableUsers.length === 0
                    ? "Tất cả người dùng đã thuộc dự án"
                    : "Tìm theo tên hoặc email thành viên từ DUT-AI SSO..."
                }
                disabled={usersLoading || isSubmittingBatch}
                className="h-9 pl-9 pr-9 text-xs bg-white border-slate-200"
              />
              <button
                type="button"
                onClick={() => setDropdownOpen((o) => !o)}
                disabled={usersLoading || isSubmittingBatch}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-0.5"
                title="Mở danh sách"
              >
                <ChevronDown
                  className={`h-4 w-4 transition-transform ${
                    dropdownOpen ? "rotate-180" : ""
                  }`}
                />
              </button>

              {dropdownOpen && (
                <div className="absolute z-30 mt-1.5 w-full rounded-xl border border-slate-200 bg-white shadow-lg overflow-hidden">
                  <div className="max-h-60 overflow-y-auto divide-y divide-slate-100">
                    {filteredAvailableUsers.length === 0 ? (
                      <div className="px-4 py-6 text-center text-xs text-slate-500">
                        {availableUsers.length === 0
                          ? "Không còn người dùng nào chưa thuộc dự án."
                          : "Không tìm thấy người dùng phù hợp."}
                      </div>
                    ) : (
                      filteredAvailableUsers.map((u) => {
                        const isSelected = selectedSet.has(u.id);
                        return (
                          <button
                            key={u.id}
                            type="button"
                            onClick={() => toggleUserSelection(u.id)}
                            className={`flex w-full items-center justify-between px-3.5 py-2.5 text-left transition-colors ${
                              isSelected
                                ? "bg-blue-50/70 hover:bg-blue-50"
                                : "hover:bg-slate-50"
                            }`}
                          >
                            <div className="flex items-center gap-3 min-w-0">
                              <Checkbox
                                checked={isSelected}
                                onCheckedChange={() =>
                                  toggleUserSelection(u.id)
                                }
                                onClick={(e) => e.stopPropagation()}
                              />
                              {u.avatar_url ? (
                                <img
                                  src={u.avatar_url}
                                  alt={u.name}
                                  className="h-7 w-7 shrink-0 rounded-full object-cover border border-slate-200"
                                />
                              ) : (
                                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-100 text-[11px] font-bold text-blue-700">
                                  {(u.name || u.email || "U")[0].toUpperCase()}
                                </div>
                              )}
                              <div className="min-w-0">
                                <p className="text-xs font-semibold text-slate-800 truncate">
                                  {u.name}
                                </p>
                                <p className="text-[11px] text-slate-500 truncate">
                                  {u.email}
                                </p>
                              </div>
                            </div>
                            {isSelected && (
                              <Check className="h-3.5 w-3.5 text-blue-600 shrink-0" />
                            )}
                          </button>
                        );
                      })
                    )}
                  </div>
                </div>
              )}
            </div>

            <Button
              size="sm"
              onClick={handleAddSelected}
              disabled={selectedUserIds.length === 0 || isSubmittingBatch}
              className="bg-blue-600 hover:bg-blue-700 text-white shrink-0 h-9 px-4"
            >
              {isSubmittingBatch ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" />
              ) : (
                <UserPlus className="h-3.5 w-3.5 mr-1.5" />
              )}
              {selectedUserIds.length > 0
                ? `Thêm (${selectedUserIds.length}) thành viên`
                : "Thêm thành viên"}
            </Button>
          </div>

          {/* Selected Users Chips */}
          {selectedUserIds.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-[11px] font-medium text-slate-500 mr-1">
                Đang chọn:
              </span>
              {selectedUserIds.map((uid) => {
                const profile = userMap.get(uid);
                return (
                  <Badge
                    key={uid}
                    variant="secondary"
                    className="bg-blue-50 text-blue-700 border border-blue-200 text-[11px] font-medium pl-2.5 pr-1 py-0.5 flex items-center gap-1"
                  >
                    <span>{profile?.name || `User #${uid}`}</span>
                    <button
                      type="button"
                      onClick={() => toggleUserSelection(uid)}
                      className="rounded-full p-0.5 hover:bg-blue-100 text-blue-600"
                      title="Bỏ chọn"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                );
              })}
              <button
                type="button"
                onClick={() => setSelectedUserIds([])}
                className="text-[11px] text-slate-400 hover:text-rose-600 ml-1"
              >
                Xóa tất cả
              </button>
            </div>
          )}
        </div>

        {/* Current Members List */}
        <div className="space-y-2.5">
          {membersLoading ? (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <Skeleton className="h-14 w-full rounded-lg" />
              <Skeleton className="h-14 w-full rounded-lg" />
            </div>
          ) : members.length === 0 ? (
            <div className="rounded-xl border-2 border-dashed border-slate-200 p-8 text-center text-xs text-slate-500">
              Chưa có thành viên nào được gán vào dự án này. (Quản trị viên hệ
              thống luôn có quyền truy cập toàn bộ dự án).
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {members.map((m) => {
                const profile = userMap.get(m.user_id);
                return (
                  <div
                    key={m.id}
                    className="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50/50 px-3.5 py-2.5"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      {profile?.avatar_url ? (
                        <img
                          src={profile.avatar_url}
                          alt={profile.name || `User #${m.user_id}`}
                          className="h-8 w-8 shrink-0 rounded-full object-cover border border-slate-200"
                        />
                      ) : (
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                          {(profile?.name || profile?.email || "U")[0].toUpperCase()}
                        </div>
                      )}
                      <div className="min-w-0">
                        <p className="text-xs font-semibold text-slate-800 truncate">
                          {profile?.name || `User #${m.user_id}`}
                        </p>
                        <p className="text-[11px] text-slate-500 truncate">
                          {profile?.email || `SSO ID: ${m.user_id}`}
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      onClick={() => handleRemove(m.user_id)}
                      disabled={removeMutation.isPending}
                      className="text-slate-400 hover:text-rose-600 hover:bg-rose-50 shrink-0"
                      title="Xóa khỏi dự án"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
