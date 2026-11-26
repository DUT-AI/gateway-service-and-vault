"use client";

import React from "react";
import { AlertTriangle, Loader2, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useDeleteSecretMutation } from "../hooks/use-vault-queries";
import type { FlatSecretItem } from "../types";

export interface DeleteSecretDialogProps {
  projectId: string;
  secret: FlatSecretItem | null;
  onClose: () => void;
}

export function DeleteSecretDialog({
  projectId,
  secret,
  onClose,
}: DeleteSecretDialogProps) {
  const deleteMutation = useDeleteSecretMutation(projectId);

  const handleConfirmDelete = async () => {
    if (!secret) return;
    try {
      await deleteMutation.mutateAsync({
        scopeName: secret.scope_name,
        key: secret.key,
      });
      toast.success(`Đã xóa biến ${secret.key} (${secret.scope_name})`);
      onClose();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail;
      toast.error(detail || "Không thể xóa biến môi trường");
    }
  };

  return (
    <Dialog open={Boolean(secret)} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-2 text-rose-600 mb-1">
            <AlertTriangle className="h-5 w-5" />
            <DialogTitle>Xác nhận xóa biến môi trường</DialogTitle>
          </div>
          <DialogDescription className="text-xs text-slate-500">
            Hành động này sẽ xóa vĩnh viễn biến môi trường và lịch sử phiên bản
            của nó khỏi Dynamic Vault.
          </DialogDescription>
        </DialogHeader>

        {secret && (
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5 my-1">
            <div className="flex justify-between">
              <span className="text-slate-500">Key:</span>
              <span className="font-mono font-semibold text-slate-900">
                {secret.key}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Scope:</span>
              <span className="font-mono text-slate-700">
                {secret.scope_name}
              </span>
            </div>
          </div>
        )}

        <DialogFooter className="pt-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onClose}
            disabled={deleteMutation.isPending}
            className="text-xs"
          >
            Hủy
          </Button>
          <Button
            type="button"
            size="sm"
            variant="destructive"
            onClick={handleConfirmDelete}
            disabled={deleteMutation.isPending}
            className="text-xs"
          >
            {deleteMutation.isPending ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" />
                Đang xóa...
              </>
            ) : (
              <>
                <Trash2 className="h-3.5 w-3.5 mr-1" />
                Xác nhận xóa
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
