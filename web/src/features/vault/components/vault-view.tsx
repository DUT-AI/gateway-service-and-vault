"use client";

import React, { useMemo, useState } from "react";
import {
  BookOpen,
  Lock,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  Terminal,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/auth-context";
import { useScopesQuery, useSecretsQuery } from "../hooks/use-vault-queries";
import { useVaultSse } from "../hooks/use-vault-sse";
import { ScopeTabs } from "./scope-tabs";
import { SecretsTable } from "./secrets-table";
import { SecretDialog } from "./secret-dialog";
import { KeyPermissionMatrixModal } from "./key-permission-matrix-modal";
import { LiveSyncStatusBadge } from "./live-sync-status-badge";
import { LiveAuditFeed } from "./live-audit-feed";
import { SdkQuickstartDialog } from "./sdk-quickstart-dialog";
import type { FlatSecretItem } from "../types";

export interface VaultViewProps {
  projectId: string;
  projectName: string;
}

export function VaultView({ projectId, projectName }: VaultViewProps) {
  const { isAdmin } = useAuth();
  const [selectedScope, setSelectedScope] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [createDialogOpen, setCreateDialogOpen] = useState<boolean>(false);
  const [editingSecret, setEditingSecret] = useState<FlatSecretItem | null>(
    null
  );
  const [permissionsModalOpen, setPermissionsModalOpen] =
    useState<boolean>(false);
  const [sdkQuickstartOpen, setSdkQuickstartOpen] = useState<boolean>(false);

  // Real-Time SSE Stream Hook
  const sseState = useVaultSse(projectId, {
    scope: selectedScope,
  });

  // Queries
  const {
    data: scopes = [],
    isLoading: scopesLoading,
    refetch: refetchScopes,
  } = useScopesQuery(projectId);

  const {
    data: secretsData,
    isLoading: secretsLoading,
    refetch: refetchSecrets,
    isRefetching,
  } = useSecretsQuery(projectId, selectedScope);

  const flatItems = useMemo(
    () => secretsData?.flatItems ?? [],
    [secretsData]
  );

  // Scope counts
  const scopeCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    flatItems.forEach((item) => {
      counts[item.scope_name] = (counts[item.scope_name] || 0) + 1;
    });
    return counts;
  }, [flatItems]);

  // Client-side search filtering
  const filteredItems = useMemo(() => {
    if (!searchQuery.trim()) return flatItems;
    const q = searchQuery.toLowerCase().trim();
    return flatItems.filter(
      (item) =>
        item.key.toLowerCase().includes(q) ||
        item.scope_name.toLowerCase().includes(q)
    );
  }, [flatItems, searchQuery]);

  // Available unique keys and scope names for dialogs
  const availableKeys = useMemo(
    () => Array.from(new Set(flatItems.map((i) => i.key))),
    [flatItems]
  );

  const availableScopes = useMemo(
    () => scopes.map((s) => s.name),
    [scopes]
  );

  const handleEdit = (item: FlatSecretItem) => {
    setEditingSecret(item);
  };

  const handleRefresh = () => {
    refetchScopes();
    refetchSecrets();
  };

  return (
    <div className="space-y-5">
      <Card className="min-h-[600px] border-slate-200 bg-white shadow-2xs">
        <CardHeader className="border-b border-slate-100 pb-4">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <CardTitle className="text-base font-semibold text-slate-900 flex items-center gap-2">
                <Lock className="h-4 w-4 text-blue-600" />
                Quản lý biến môi trường bảo mật (Dynamic Vault)
              </CardTitle>
              <p className="text-xs text-slate-500 mt-1">
                Các biến môi trường được mã hóa AES-256-GCM và phân phối trực
                tiếp vào bộ nhớ tiến trình ứng dụng.
              </p>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <LiveSyncStatusBadge
                status={sseState.status}
                lastPing={sseState.lastPing}
                onReconnect={sseState.reconnect}
              />

              <LiveAuditFeed
                events={sseState.events}
                isPaused={sseState.isPaused}
                onTogglePause={sseState.togglePause}
                onClearHistory={sseState.clearHistory}
              />

              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={secretsLoading || isRefetching}
                className="text-slate-600 border-slate-200"
                title="Làm mới dữ liệu"
              >
                <RefreshCw
                  className={`h-3.5 w-3.5 ${
                    isRefetching ? "animate-spin" : ""
                  }`}
                />
                <span className="hidden sm:inline ml-1">Làm mới</span>
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setSdkQuickstartOpen(true)}
                className="border-slate-200 text-slate-700 hover:bg-slate-50"
              >
                <Terminal className="h-3.5 w-3.5 mr-1.5 text-blue-600" />
                Hướng dẫn dùng Env / SDK
              </Button>

              {isAdmin && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPermissionsModalOpen(true)}
                  className="border-slate-200 text-slate-700 hover:bg-slate-50"
                >
                  <ShieldCheck className="h-3.5 w-3.5 mr-1.5 text-emerald-600" />
                  Phân quyền truy cập
                </Button>
              )}

              <Button
                size="sm"
                onClick={() => {
                  setEditingSecret(null);
                  setCreateDialogOpen(true);
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium"
              >
                <Plus className="h-4 w-4 mr-1.5" />
                Thêm biến mới
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4 pt-4">
          {/* Quick Inline Guidance Banner */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 rounded-xl border border-blue-100 bg-blue-50/50 px-3.5 py-2.5 text-xs">
            <div className="flex items-center gap-2 text-slate-700">
              <BookOpen className="h-4 w-4 text-blue-600 shrink-0" />
              <span>
                Nạp các biến này trực tiếp vào RAM (
                <code className="font-mono bg-white px-1 rounded border border-blue-100">
                  os.environ
                </code>
                ) bằng <strong className="text-slate-900">dut-vault run</strong>{" "}
                hoặc <strong className="text-slate-900">VaultClient</strong> mà
                không cần tạo file{" "}
                <code className="font-mono bg-white px-1 rounded border border-blue-100">
                  .env
                </code>
                .
              </span>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setSdkQuickstartOpen(true)}
              className="h-7 px-2.5 text-[11px] bg-white border-blue-200 text-blue-700 hover:bg-blue-100 shrink-0"
            >
              Xem code mẫu & CLI
            </Button>
          </div>

          {/* Filter Bar & Scope Switcher */}
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <ScopeTabs
              scopes={scopes}
              selectedScope={selectedScope}
              onSelectScope={setSelectedScope}
              scopeCounts={scopeCounts}
              totalCount={flatItems.length}
            />

            <div className="relative w-full sm:w-64">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
              <Input
                placeholder="Tìm theo Key hoặc Scope..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="h-8 pl-8 pr-7 text-xs bg-slate-50/50"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
          </div>

          {/* Secrets Data Table */}
          <SecretsTable
            items={filteredItems}
            isLoading={secretsLoading || scopesLoading}
            highlightedKeys={sseState.highlightedKeys}
            onEditSecret={handleEdit}
            onCreateSecret={() => {
              setEditingSecret(null);
              setCreateDialogOpen(true);
            }}
          />
        </CardContent>
      </Card>

      {/* Secret Creation & Edit Dialog */}
      <SecretDialog
        projectId={projectId}
        open={createDialogOpen || Boolean(editingSecret)}
        onOpenChange={(open) => {
          if (!open) {
            setCreateDialogOpen(false);
            setEditingSecret(null);
          }
        }}
        availableScopes={availableScopes}
        initialData={editingSecret}
      />

      {/* Granular Key Permissions Matrix Modal */}
      <KeyPermissionMatrixModal
        projectId={projectId}
        projectName={projectName}
        open={permissionsModalOpen}
        onOpenChange={setPermissionsModalOpen}
        availableKeys={availableKeys}
      />

      {/* Zero-.env SDK Quickstart Dialog */}
      <SdkQuickstartDialog
        projectId={projectId}
        projectName={projectName}
        selectedScope={selectedScope}
        open={sdkQuickstartOpen}
        onOpenChange={setSdkQuickstartOpen}
      />
    </div>
  );
}
