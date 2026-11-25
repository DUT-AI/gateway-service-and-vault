"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Eye,
  EyeOff,
  Globe,
  KeyRound,
  Loader2,
  Lock,
  Plus,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
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
import { NativeSelect } from "@/components/ui/native-select";
import { useCreateServiceMutation } from "../hooks/use-services-queries";
import {
  createServiceSchema,
  generateSlug,
  type CreateServiceFormData,
} from "../types/form-schemas";

export interface CreateServiceDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateServiceDialog({
  open,
  onOpenChange,
}: CreateServiceDialogProps) {
  const [showCredential, setShowCredential] = useState(false);
  const [slugManuallyEdited, setSlugManuallyEdited] = useState(false);
  const createMutation = useCreateServiceMutation();

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    watch,
    formState: { errors },
  } = useForm<CreateServiceFormData>({
    resolver: zodResolver(createServiceSchema),
    defaultValues: {
      name: "",
      slug: "",
      base_url: "",
      auth_type: "BEARER_TOKEN",
      credential: "",
      timeout_seconds: 30,
    },
  });

  const selectedAuthType = watch("auth_type");

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      reset();
      setShowCredential(false);
      setSlugManuallyEdited(false);
    }
    onOpenChange(nextOpen);
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newName = e.target.value;
    if (!slugManuallyEdited) {
      setValue("slug", generateSlug(newName), { shouldValidate: true });
    }
  };

  const onSubmit = async (data: CreateServiceFormData) => {
    try {
      await createMutation.mutateAsync({
        name: data.name.trim(),
        slug: data.slug.trim(),
        base_url: data.base_url.trim(),
        auth_type: data.auth_type,
        credential: data.credential,
        timeout_seconds: Number(data.timeout_seconds),
      });

      toast.success(`Đã khai báo dịch vụ "${data.name}" thành công!`);
      reset();
      setShowCredential(false);
      setSlugManuallyEdited(false);
      onOpenChange(false);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Đã xảy ra lỗi khi khai báo dịch vụ upstream";
      toast.error(msg);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
              <Globe className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold text-slate-900">
                Khai báo dịch vụ Upstream mới
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500">
                Cấu hình dịch vụ đối tác và bảo vệ thông tin xác thực tại Gateway.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-1">
          {/* Service Name */}
          <div className="space-y-1.5">
            <Label
              htmlFor="service-name"
              className="text-xs font-semibold text-slate-700"
            >
              Tên dịch vụ đối tác <span className="text-rose-500">*</span>
            </Label>
            <Input
              id="service-name"
              placeholder="VD: OpenAI API Platform, Cổng Thanh Toán VNPay..."
              className="text-xs h-9 bg-white"
              {...register("name", {
                onChange: handleNameChange,
              })}
            />
            {errors.name && (
              <p className="text-[11px] text-rose-600 font-medium">
                {errors.name.message}
              </p>
            )}
          </div>

          {/* Service Slug */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <Label
                htmlFor="service-slug"
                className="text-xs font-semibold text-slate-700"
              >
                Mã định danh (Slug) <span className="text-rose-500">*</span>
              </Label>
              <span className="text-[10px] text-slate-400">
                Được sử dụng cho URL định tuyến tại Gateway
              </span>
            </div>
            <div className="relative">
              <Input
                id="service-slug"
                placeholder="VD: openai-api-platform"
                className="text-xs h-9 font-mono bg-slate-50 text-slate-800"
                {...register("slug", {
                  onChange: () => setSlugManuallyEdited(true),
                })}
              />
              <Sparkles className="absolute right-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-blue-500 pointer-events-none" />
            </div>
            {errors.slug && (
              <p className="text-[11px] text-rose-600 font-medium">
                {errors.slug.message}
              </p>
            )}
          </div>

          {/* Base URL */}
          <div className="space-y-1.5">
            <Label
              htmlFor="service-url"
              className="text-xs font-semibold text-slate-700"
            >
              Base URL đích (Upstream Endpoint) <span className="text-rose-500">*</span>
            </Label>
            <Input
              id="service-url"
              placeholder="https://api.openai.com/v1"
              className="text-xs h-9 font-mono bg-white"
              {...register("base_url")}
            />
            {errors.base_url && (
              <p className="text-[11px] text-rose-600 font-medium">
                {errors.base_url.message}
              </p>
            )}
            <p className="text-[10px] text-slate-500">
              Địa chỉ endpoint thực tế của nhà cung cấp dịch vụ phía sau Gateway.
            </p>
          </div>

          {/* Auth Type & Timeout Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Auth Type */}
            <div className="space-y-1.5">
              <Label
                htmlFor="service-auth"
                className="text-xs font-semibold text-slate-700"
              >
                Phương thức xác thực
              </Label>
              <NativeSelect id="service-auth" {...register("auth_type")}>
                <option value="BEARER_TOKEN">Bearer Token (Header)</option>
                <option value="API_KEY">API Key (X-API-Key)</option>
                <option value="BASIC_AUTH">Basic Authentication</option>
                <option value="NO_AUTH">Không cần xác thực (No Auth)</option>
              </NativeSelect>
              {errors.auth_type && (
                <p className="text-[11px] text-rose-600 font-medium">
                  {errors.auth_type.message}
                </p>
              )}
            </div>

            {/* Timeout */}
            <div className="space-y-1.5">
              <Label
                htmlFor="service-timeout"
                className="text-xs font-semibold text-slate-700"
              >
                Thời gian chờ (Timeout)
              </Label>
              <NativeSelect
                id="service-timeout"
                {...register("timeout_seconds", { valueAsNumber: true })}
              >
                <option value={5}>5 giây (Phản hồi nhanh)</option>
                <option value={15}>15 giây</option>
                <option value={30}>30 giây (Mặc định)</option>
                <option value={60}>60 giây (Mô hình AI / LLM)</option>
                <option value={120}>120 giây (Tác vụ dài)</option>
              </NativeSelect>
              {errors.timeout_seconds && (
                <p className="text-[11px] text-rose-600 font-medium">
                  {errors.timeout_seconds.message}
                </p>
              )}
            </div>
          </div>

          {/* Upstream Credential */}
          {selectedAuthType !== "NO_AUTH" && (
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label
                  htmlFor="service-cred"
                  className="text-xs font-semibold text-slate-700 flex items-center gap-1.5"
                >
                  <Lock className="h-3.5 w-3.5 text-blue-600" />
                  Khóa bí mật đối tác (Credential Token){" "}
                  <span className="text-rose-500">*</span>
                </Label>
                <span className="text-[10px] text-emerald-600 font-medium flex items-center gap-1">
                  <ShieldCheck className="h-3 w-3" />
                  Mã hóa AES-256-GCM tại Backend
                </span>
              </div>
              <div className="relative">
                <Input
                  id="service-cred"
                  type={showCredential ? "text" : "password"}
                  placeholder="sk-proj-... hoặc api_key_secret"
                  className="text-xs h-9 font-mono pr-9 bg-white"
                  {...register("credential")}
                />
                <button
                  type="button"
                  onClick={() => setShowCredential(!showCredential)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  title={showCredential ? "Ẩn khóa bí mật" : "Hiện khóa bí mật"}
                >
                  {showCredential ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
              {errors.credential && (
                <p className="text-[11px] text-rose-600 font-medium">
                  {errors.credential.message}
                </p>
              )}
              <p className="text-[10px] text-slate-500 leading-relaxed">
                Token gốc này được Gateway tự động tiêm (inject) vào request chuyển
                tiếp, giúp lập trình viên không bao giờ chạm đến khóa bí mật của tổ chức.
              </p>
            </div>
          )}

          <DialogFooter className="pt-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => handleOpenChange(false)}
              disabled={createMutation.isPending}
              className="text-xs"
            >
              Hủy
            </Button>
            <Button
              type="submit"
              size="sm"
              disabled={createMutation.isPending}
              className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium"
            >
              {createMutation.isPending ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" />
                  Đang lưu và mã hóa...
                </>
              ) : (
                <>
                  <Plus className="h-3.5 w-3.5 mr-1" />
                  Lưu dịch vụ upstream
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
