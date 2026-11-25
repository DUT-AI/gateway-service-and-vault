"use client";

import React, { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  ClipboardPaste,
  Eye,
  EyeOff,
  FileUp,
  Loader2,
  Lock,
  Plus,
  Sparkles,
  Trash2,
} from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
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
import {
  useSaveSecretMutation,
  useSaveSecretsBatchMutation,
} from "../hooks/use-vault-queries";
import { parseEnvContent } from "../utils/parse-env";
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

interface DraftSecretRow {
  id: string;
  key: string;
  value: string;
}

function createEmptyRow(): DraftSecretRow {
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    key: "",
    value: "",
  };
}

export function SecretDialog({
  projectId,
  open,
  onOpenChange,
  availableScopes = [],
  initialData,
}: SecretDialogProps) {
  const isEditMode = Boolean(initialData);
  const [showValue, setShowValue] = useState(false);

  // Batch create states
  const [scopeName, setScopeName] = useState<string>(
    availableScopes[0] || "Common"
  );
  const [rows, setRows] = useState<DraftSecretRow[]>([createEmptyRow()]);
  const [batchError, setBatchError] = useState<string | null>(null);
  const [showPasteBox, setShowPasteBox] = useState(false);
  const [pasteText, setPasteText] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const saveMutation = useSaveSecretMutation(projectId);
  const saveBatchMutation = useSaveSecretsBatchMutation(projectId);

  // Single-edit form (react-hook-form)
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
      setScopeName(availableScopes[0] || "Common");
      setRows([createEmptyRow()]);
      setBatchError(null);
      setShowPasteBox(false);
      setPasteText("");
    }
    setShowValue(false);
  }, [initialData, availableScopes, reset, open]);

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      reset();
      setShowValue(false);
      setBatchError(null);
      setShowPasteBox(false);
      setPasteText("");
    }
    onOpenChange(nextOpen);
  };

  // Single edit submit
  const onSubmitEdit = async (data: CreateSecretInput) => {
    try {
      await saveMutation.mutateAsync({
        scope_name: data.scope_name.trim(),
        key: data.key.trim().toUpperCase(),
        value: data.value,
      });
      toast.success(`Đã cập nhật biến ${data.key} thành công!`);
      handleOpenChange(false);
    } catch (err: any) {
      toast.error(
        err?.response?.data?.detail ||
          err?.message ||
          "Không thể lưu biến môi trường"
      );
    }
  };

  // Apply parsed .env entries into draft rows
  const applyParsedEntries = (rawContent: string, sourceLabel: string) => {
    const parsed = parseEnvContent(rawContent);
    if (parsed.length === 0) {
      toast.error(
        `Không tìm thấy biến hợp lệ (KEY=VALUE) nào trong ${sourceLabel}.`
      );
      return;
    }

    setRows((prev) => {
      const existingNonEmpty = prev.filter(
        (r) => r.key.trim() !== "" || r.value.trim() !== ""
      );
      const mergedMap = new Map<string, DraftSecretRow>();
      existingNonEmpty.forEach((r) => {
        mergedMap.set(r.key.trim().toUpperCase(), r);
      });
      parsed.forEach((entry) => {
        const existing = mergedMap.get(entry.key);
        mergedMap.set(entry.key, {
          id: existing?.id || `${Date.now()}-${entry.key}`,
          key: entry.key,
          value: entry.value,
        });
      });
      return Array.from(mergedMap.values());
    });
    setBatchError(null);
    toast.success(`Đã trích xuất ${parsed.length} biến từ ${sourceLabel}!`);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      applyParsedEntries(text, file.name);
    } catch {
      toast.error("Không thể đọc nội dung file .env");
    } finally {
      e.target.value = "";
    }
  };

  const handleExtractPaste = () => {
    if (!pasteText.trim()) return;
    applyParsedEntries(pasteText, "nội dung vừa dán");
    setPasteText("");
    setShowPasteBox(false);
  };

  const handleKeyPaste = (
    rowIndex: number,
    e: React.ClipboardEvent<HTMLInputElement>
  ) => {
    const text = e.clipboardData.getData("text");
    if (text.includes("=") && (text.includes("\n") || rowIndex === 0)) {
      const parsed = parseEnvContent(text);
      if (parsed.length >= 1) {
        e.preventDefault();
        applyParsedEntries(text, "clipboard");
      }
    }
  };

  const updateRow = (
    id: string,
    field: "key" | "value",
    nextValue: string
  ) => {
    setBatchError(null);
    setRows((prev) =>
      prev.map((row) =>
        row.id === id
          ? {
              ...row,
              [field]: field === "key" ? nextValue.toUpperCase() : nextValue,
            }
          : row
      )
    );
  };

  const removeRow = (id: string) => {
    setRows((prev) => (prev.length > 1 ? prev.filter((r) => r.id !== id) : prev));
  };

  const handleSubmitBatch = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedScope = scopeName.trim();
    if (!trimmedScope) {
      setBatchError("Vui lòng nhập tên Nhóm cấu hình (Scope).");
      return;
    }

    const cleanedItems = rows.map((r) => ({
      key: r.key.trim().toUpperCase(),
      value: r.value,
    }));

    for (let i = 0; i < cleanedItems.length; i++) {
      const item = cleanedItems[i];
      if (!item.key || !/^[A-Z0-9_]{2,}$/.test(item.key)) {
        setBatchError(
          `Dòng #${i + 1}: Tên Key không hợp lệ (chỉ dùng chữ in hoa, số, dấu gạch dưới "_", tối thiểu 2 ký tự).`
        );
        return;
      }
      if (!item.value) {
        setBatchError(`Dòng #${i + 1} (${item.key}): Giá trị không được để trống.`);
        return;
      }
    }

    try {
      await saveBatchMutation.mutateAsync({
        scope_name: trimmedScope,
        items: cleanedItems,
      });
      toast.success(
        cleanedItems.length === 1
          ? `Đã tạo biến ${cleanedItems[0].key} thành công!`
          : `Đã mã hóa và lưu ${cleanedItems.length} biến môi trường thành công!`
      );
      handleOpenChange(false);
    } catch (err: any) {
      toast.error(
        err?.response?.data?.detail ||
          err?.message ||
          "Không thể lưu các biến môi trường"
      );
    }
  };

  const isPending = saveMutation.isPending || saveBatchMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className={isEditMode ? "sm:max-w-md" : "sm:max-w-2xl"}>
        {isEditMode ? (
          <form onSubmit={handleSubmit(onSubmitEdit)} className="space-y-4">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-base sm:text-lg font-bold text-slate-900">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                  <Lock className="h-4 w-4" />
                </div>
                Chỉnh sửa biến môi trường
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500">
                Giá trị sẽ được mã hóa chuẩn authenticated AES-256-GCM tại máy chủ.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-3.5 py-1">
              <div className="space-y-1.5">
                <Label htmlFor="secret-scope" className="text-xs font-semibold">
                  Nhóm cấu hình (Scope) <span className="text-rose-500">*</span>
                </Label>
                <Input
                  id="secret-scope"
                  list="scope-options"
                  {...register("scope_name")}
                  className={errors.scope_name ? "border-rose-300" : ""}
                />
                <datalist id="scope-options">
                  {availableScopes.map((scope) => (
                    <option key={scope} value={scope} />
                  ))}
                </datalist>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="secret-key" className="text-xs font-semibold">
                  Tên Key <span className="text-rose-500">*</span>
                </Label>
                <Input
                  id="secret-key"
                  {...register("key", {
                    onChange: (e) =>
                      setValue("key", e.target.value.toUpperCase()),
                  })}
                  disabled
                  className="font-mono text-xs"
                />
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
                disabled={isPending}
              >
                Hủy
              </Button>
              <Button
                type="submit"
                disabled={isPending}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium"
              >
                {isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-1.5 animate-spin" />
                    Đang lưu...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-1.5" />
                    Lưu thay đổi
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        ) : (
          <form onSubmit={handleSubmitBatch} className="space-y-4">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-base sm:text-lg font-bold text-slate-900">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                  <Lock className="h-4 w-4" />
                </div>
                Thêm biến môi trường
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500">
                Thêm một hoặc nhiều biến cùng lúc, hoặc nạp trực tiếp file{" "}
                <span className="font-mono font-semibold text-slate-700">.env</span>{" "}
                để hệ thống tự động trích xuất.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-1">
              {/* Scope + .env Import Toolbar */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 items-end">
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <Label
                      htmlFor="batch-scope"
                      className="text-xs font-semibold"
                    >
                      Nhóm cấu hình (Scope){" "}
                      <span className="text-rose-500">*</span>
                    </Label>
                    <span className="text-[11px] text-slate-400">
                      Chọn hoặc gõ tên mới
                    </span>
                  </div>
                  <Input
                    id="batch-scope"
                    list="batch-scope-options"
                    placeholder="Ví dụ: Common, Database, Payment..."
                    value={scopeName}
                    onChange={(e) => {
                      setScopeName(e.target.value);
                      setBatchError(null);
                    }}
                  />
                  <datalist id="batch-scope-options">
                    {availableScopes.map((scope) => (
                      <option key={scope} value={scope} />
                    ))}
                  </datalist>
                </div>

                <div className="flex items-center gap-2 sm:justify-end">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".env,.env.*,text/plain"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                    className="text-xs border-slate-200 text-slate-700 hover:bg-slate-50"
                  >
                    <FileUp className="h-3.5 w-3.5 mr-1.5 text-blue-600" />
                    Nạp file .env
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setShowPasteBox((v) => !v)}
                    className="text-xs border-slate-200 text-slate-700 hover:bg-slate-50"
                  >
                    <ClipboardPaste className="h-3.5 w-3.5 mr-1.5 text-emerald-600" />
                    Dán .env
                  </Button>
                </div>
              </div>

              {/* Quick Paste .env Box */}
              {showPasteBox && (
                <div className="rounded-xl border border-blue-200 bg-blue-50/40 p-3 space-y-2">
                  <Label className="text-xs font-semibold text-slate-700">
                    Dán nội dung file .env vào đây (KEY=VALUE mỗi dòng)
                  </Label>
                  <textarea
                    rows={4}
                    value={pasteText}
                    onChange={(e) => setPasteText(e.target.value)}
                    placeholder={`DATABASE_URL=postgresql://user:pass@localhost:5432/db\nJWT_SECRET=super_secret_key`}
                    className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-xs font-mono text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                  />
                  <div className="flex justify-end gap-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowPasteBox(false)}
                    >
                      Đóng
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      onClick={handleExtractPaste}
                      disabled={!pasteText.trim()}
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      Trích xuất biến
                    </Button>
                  </div>
                </div>
              )}

              {/* Key-Value Rows Header */}
              <div className="flex items-center justify-between pt-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-700">
                    Danh sách biến
                  </span>
                  <Badge
                    variant="secondary"
                    className="bg-slate-100 text-slate-700 text-[11px]"
                  >
                    {rows.length} biến
                  </Badge>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => setShowValue((v) => !v)}
                    className="inline-flex items-center gap-1 text-[11px] text-blue-600 hover:text-blue-700"
                  >
                    {showValue ? (
                      <>
                        <EyeOff className="h-3 w-3" />
                        Ẩn tất cả giá trị
                      </>
                    ) : (
                      <>
                        <Eye className="h-3 w-3" />
                        Hiện tất cả giá trị
                      </>
                    )}
                  </button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setRows((prev) => [...prev, createEmptyRow()])}
                    className="h-7 px-2.5 text-xs border-slate-200"
                  >
                    <Plus className="h-3.5 w-3.5 mr-1" />
                    Thêm dòng
                  </Button>
                </div>
              </div>

              {/* Scrollable Key-Value Rows */}
              <div className="max-h-64 overflow-y-auto space-y-2 pr-1">
                {rows.map((row, idx) => (
                  <div
                    key={row.id}
                    className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50/50 p-2"
                  >
                    <Input
                      value={row.key}
                      onChange={(e) => updateRow(row.id, "key", e.target.value)}
                      onPaste={(e) => handleKeyPaste(idx, e)}
                      placeholder="KEY_NAME"
                      className="h-8 w-[42%] bg-white font-mono text-xs"
                    />
                    <Input
                      type={showValue ? "text" : "password"}
                      value={row.value}
                      onChange={(e) =>
                        updateRow(row.id, "value", e.target.value)
                      }
                      placeholder="Giá trị bảo mật..."
                      className="h-8 flex-1 bg-white font-mono text-xs"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-sm"
                      onClick={() => removeRow(row.id)}
                      disabled={rows.length === 1}
                      className="text-slate-400 hover:text-rose-600 hover:bg-rose-50 shrink-0"
                      title="Xóa dòng"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                ))}
              </div>

              {batchError && (
                <p className="text-xs font-medium text-rose-600 bg-rose-50 border border-rose-200 rounded-lg px-3 py-2">
                  {batchError}
                </p>
              )}
            </div>

            <DialogFooter className="gap-2 sm:gap-0 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => handleOpenChange(false)}
                disabled={isPending}
              >
                Hủy
              </Button>
              <Button
                type="submit"
                disabled={isPending}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium"
              >
                {isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-1.5 animate-spin" />
                    Đang mã hóa & lưu...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-1.5" />
                    Lưu {rows.length} biến môi trường
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
