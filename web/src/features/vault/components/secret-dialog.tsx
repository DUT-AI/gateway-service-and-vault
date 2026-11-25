"use client";

import React from "react";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import type { FlatSecretItem } from "../types";
import { SecretBatchForm } from "./secret-batch-form";
import { SecretEditForm } from "./secret-edit-form";

export interface SecretDialogProps {
  projectId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  availableScopes?: string[];
  initialData?: FlatSecretItem | null;
}

export function SecretDialog({
  projectId,
  open,
  onOpenChange,
  availableScopes = [],
  initialData,
}: SecretDialogProps) {
  const isEditMode = Boolean(initialData);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className={isEditMode ? "sm:max-w-md" : "sm:max-w-2xl"}>
        {initialData ? (
          <SecretEditForm
            key={`${initialData.scope_name}:${initialData.key}:${String(open)}`}
            projectId={projectId}
            availableScopes={availableScopes}
            initialData={initialData}
            onClose={() => onOpenChange(false)}
          />
        ) : (
          <SecretBatchForm
            key={`batch:${String(open)}`}
            projectId={projectId}
            availableScopes={availableScopes}
            onClose={() => onOpenChange(false)}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}
