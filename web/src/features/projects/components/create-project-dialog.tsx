"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Plus, Sparkles } from "lucide-react";
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
import { useCreateProjectMutation } from "../hooks/use-projects-queries";
import {
  createProjectSchema,
  generateSlug,
  type CreateProjectInput,
} from "../types/form-schemas";

export interface CreateProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateProjectDialog({
  open,
  onOpenChange,
}: CreateProjectDialogProps) {
  const [slugManuallyEdited, setSlugManuallyEdited] = useState(false);
  const createMutation = useCreateProjectMutation();

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<CreateProjectInput>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: "",
      slug: "",
      description: "",
    },
  });

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      reset();
      setSlugManuallyEdited(false);
    }
    onOpenChange(nextOpen);
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    if (!slugManuallyEdited) {
      setValue("slug", generateSlug(val), { shouldValidate: true });
    }
  };

  const onSubmit = async (data: CreateProjectInput) => {
    try {
      await createMutation.mutateAsync({
        name: data.name,
        slug: data.slug,
        description: data.description?.trim() || null,
      });
      toast.success("Dự án đã được tạo thành công!");
      handleOpenChange(false);
    } catch (err: any) {
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Đã xảy ra lỗi khi tạo dự án";
      toast.error(detail);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-lg font-bold text-slate-900">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#EEF3FA] text-[#042B5F]">
                <Plus className="h-4 w-4" />
              </div>
              Tạo dự án mới
            </DialogTitle>
            <DialogDescription className="text-xs text-slate-500">
              Thiết lập không gian làm việc để quản lý biến môi trường Vault và
              Virtual Keys.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3.5 py-1">
            <div className="space-y-1.5">
              <Label htmlFor="project-name" className="text-xs font-semibold">
                Tên dự án <span className="text-rose-500">*</span>
              </Label>
              <Input
                id="project-name"
                placeholder="Ví dụ: Core Banking Gateway"
                {...register("name", {
                  onChange: handleNameChange,
                })}
                className={errors.name ? "border-rose-300" : ""}
              />
              {errors.name && (
                <p className="text-[11px] text-rose-500 font-medium">
                  {errors.name.message}
                </p>
              )}
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="project-slug" className="text-xs font-semibold">
                  Mã định danh (Slug) <span className="text-rose-500">*</span>
                </Label>
                <span className="text-[11px] text-slate-400">
                  Tự động gợi ý
                </span>
              </div>
              <Input
                id="project-slug"
                placeholder="core-banking-gateway"
                {...register("slug", {
                  onChange: () => setSlugManuallyEdited(true),
                })}
                className={`font-mono text-xs ${
                  errors.slug ? "border-rose-300" : ""
                }`}
              />
              {errors.slug ? (
                <p className="text-[11px] text-rose-500 font-medium">
                  {errors.slug.message}
                </p>
              ) : (
                <p className="text-[11px] text-slate-400">
                  Chỉ gồm chữ thường, số và gạch ngang (-). Dùng cho định tuyến và
                  API.
                </p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label
                htmlFor="project-description"
                className="text-xs font-semibold"
              >
                Mô tả dự án <span className="text-slate-400 font-normal">(Tùy chọn)</span>
              </Label>
              <Input
                id="project-description"
                placeholder="Mô tả mục đích và phạm vi của dự án..."
                {...register("description")}
                className={errors.description ? "border-rose-300" : ""}
              />
              {errors.description && (
                <p className="text-[11px] text-rose-500 font-medium">
                  {errors.description.message}
                </p>
              )}
            </div>
          </div>

          <DialogFooter className="gap-2 sm:gap-0 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={createMutation.isPending}
            >
              Hủy
            </Button>
            <Button
              type="submit"
              disabled={createMutation.isPending}
              className="bg-[#042B5F] hover:bg-[#031F46] text-white font-medium"
            >
              {createMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-1.5 animate-spin" />
                  Đang tạo...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-1.5" />
                  Tạo dự án
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
