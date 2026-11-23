"use client";

import React, { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, Key, Loader2, Lock, Sparkles } from "lucide-react";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useSaveSecretMutation } from "../hooks/use-vault-queries";
import {
  createSecretSchema,
  type CreateSecretInput,
  type FlatSecretItem,
} from "../types";

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
  const [showValue, setShowValue] = useState(false);
  const saveMutation = useSaveSecretMutation(projectId);

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<CreateSecretInput>({
    resolver: zodResolver(createSecretSchema),
    defaultValues: {
      scope_name: "Common",
      key: "",
      value: "",
    },
  });

  useEffect(() => {
    if (initialData) {
      reset({
        scope_name: initialData.scope_name,
        key: initialData.key,
        value: initialData.value,
      });
    } else {
      reset({
        scope_name: availableScopes[0] || "Common",
        key: "",
        value: "",
      });
    }
    setShowValue(false);
  }, [initialData, availableScopes, reset]);

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      reset();
      setShowValue(false);
    }
    onOpenChange(nextOpen);
  };

  const onSubmit = async (data: CreateSecretInput) => {
    try {
      await saveMutation.mutateAsync({
        scope_name: data.scope_name.trim(),
        key: data.key.trim().toUpperCase(),
        value: data.value,
      });
      toast.success(
        initialData
          ? `Đã cập nhật biến ${data.key} thành công!`
          : `Đã tạo biến ${data.key} thành công!`
      );
      handleOpenChange(false);
    } catch (err: any) {
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Không thể lưu biến môi trường";
      toast.error(detail);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-base sm:text-lg font-bold text-slate-900">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                <Lock className="h-4 w-4" />
              </div>
              {initialData ? "Chỉnh sửa biến môi trường" : "Thêm biến môi trường"}
            </DialogTitle>
            <DialogDescription className="text-xs text-slate-500">
              Giá trị sẽ được mã hóa chuẩn authenticated AES-256-GCM tại máy chủ.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3.5 py-1">
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="secret-scope" className="text-xs font-semibold">
                  Nhóm cấu hình (Scope) <span className="text-rose-500">*</span>
                </Label>
                <span className="text-[11px] text-slate-400">
                  Chọn hoặc gõ tên mới
                </span>
              </div>
              <Input
                id="secret-scope"
                list="scope-options"
                placeholder="Ví dụ: Common, Database, Payment..."
                {...register("scope_name")}
                className={errors.scope_name ? "border-rose-300" : ""}
              />
              <datalist id="scope-options">
                {availableScopes.map((scope) => (
                  <option key={scope} value={scope} />
                ))}
              </datalist>
              {errors.scope_name && (
                <p className="text-[11px] text-rose-500 font-medium">
                  {errors.scope_name.message}
                </p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="secret-key" className="text-xs font-semibold">
                Tên Key <span className="text-rose-500">*</span>
              </Label>
              <Input
                id="secret-key"
                placeholder="DATABASE_URL, JWT_SECRET..."
                {...register("key", {
                  onChange: (e) =>
                    setValue("key", e.target.value.toUpperCase()),
                })}
                disabled={Boolean(initialData)}
                className={`font-mono text-xs ${
                  errors.key ? "border-rose-300" : ""
                }`}
              />
              {errors.key ? (
                <p className="text-[11px] text-rose-500 font-medium">
                  {errors.key.message}
                </p>
              ) : (
                <p className="text-[11px] text-slate-400">
                  Quy ước viết hoa (UPPER_SNAKE_CASE).
                </p>
              )}
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="secret-value" className="text-xs font-semibold">
                  Giá trị bảo mật <span className="text-rose-500">*</span>
                </Label>
                <button
                  type="button"
                  onClick={() => setShowValue(!showValue)}
                  className="inline-flex items-center gap-1 text-[11px] text-blue-600 hover:text-blue-700"
                >
                  {showValue ? (
                    <>
                      <EyeOff className="h-3 w-3" />
                      Ẩn giá trị
                    </>
                  ) : (
                    <>
                      <Eye className="h-3 w-3" />
                      Hiện giá trị
                    </>
                  )}
                </button>
              </div>
              <textarea
                id="secret-value"
                rows={3}
                placeholder="Nhập giá trị bí mật cần mã hóa..."
                {...register("value")}
                className={`w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-xs font-mono text-slate-900 shadow-2xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 ${
                  errors.value ? "border-rose-300" : ""
                } ${!showValue ? "text-security-disc font-mono" : ""}`}
              />
              {errors.value && (
                <p className="text-[11px] text-rose-500 font-medium">
                  {errors.value.message}
                </p>
              )}
            </div>
          </div>

          <DialogFooter className="gap-2 sm:gap-0 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={saveMutation.isPending}
            >
              Hủy
            </Button>
            <Button
              type="submit"
              disabled={saveMutation.isPending}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium"
            >
              {saveMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-1.5 animate-spin" />
                  Đang lưu...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-1.5" />
                  Lưu biến môi trường
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
