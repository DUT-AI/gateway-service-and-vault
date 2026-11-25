"use client";

import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Laptop, Loader2, Plus, Server, ShieldPlus } from "lucide-react";
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
import { useAuth } from "@/contexts/auth-context";
import { useRegisterClientMutation } from "../hooks/use-clients-queries";
import {
  registerClientSchema,
  type RegisterClientFormData,
} from "../types/form-schemas";
import type { RegisterClientResult } from "../types";

export interface RegisterClientDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: (result: RegisterClientResult) => void;
}

export function RegisterClientDialog({
  open,
  onOpenChange,
  onSuccess,
}: RegisterClientDialogProps) {
  const { user } = useAuth();
  const registerMutation = useRegisterClientMutation();

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<RegisterClientFormData>({
    resolver: zodResolver(registerClientSchema),
    defaultValues: {
      name: "",
      client_type: "USER_DEVICE",
      validity_days: 30,
    },
  });

  const selectedType = watch("client_type");

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      reset();
    }
    onOpenChange(nextOpen);
  };

  const onSubmit = async (data: RegisterClientFormData) => {
    if (!user?.id) {
      toast.error("Không tìm thấy thông tin phiên người dùng. Vui lòng đăng nhập lại.");
      return;
    }

    try {
      const result = await registerMutation.mutateAsync({
        name: data.name.trim(),
        client_type: data.client_type,
        validity_days: Number(data.validity_days),
        owner_id: String(user.id),
      });

      toast.success("Đăng ký thiết bị và cấp chứng chỉ mTLS thành công!");
      reset();
      onOpenChange(false);
      onSuccess(result);
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : "Đã xảy ra lỗi khi đăng ký thiết bị mTLS";
      toast.error(message);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
              <ShieldPlus className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold text-slate-900">
                Đăng ký thiết bị & Cấp chứng chỉ mTLS
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500">
                Tạo định danh phần cứng/server và sinh cặp khóa chứng chỉ X.509.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-1">
          {/* Device Name */}
          <div className="space-y-1.5">
            <Label htmlFor="client-name" className="text-xs font-semibold text-slate-700">
              Tên thiết bị / Máy chủ <span className="text-rose-500">*</span>
            </Label>
            <Input
              id="client-name"
              placeholder="VD: MacBook Pro M3, Docker Staging-01..."
              className="text-xs h-9 bg-white"
              {...register("name")}
            />
            {errors.name && (
              <p className="text-[11px] text-rose-600 font-medium">
                {errors.name.message}
              </p>
            )}
            <p className="text-[11px] text-slate-500">
              Tên nhận diện máy trạm của lập trình viên hoặc máy chủ triển khai.
            </p>
          </div>

          {/* Client Type */}
          <div className="space-y-1.5">
            <Label htmlFor="client-type" className="text-xs font-semibold text-slate-700">
              Loại Client
            </Label>
            <div className="grid grid-cols-2 gap-2">
              <label
                className={`flex items-center gap-2.5 p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                  selectedType === "USER_DEVICE"
                    ? "border-blue-600 bg-blue-50/50 text-blue-900 font-semibold"
                    : "border-slate-200 hover:bg-slate-50 text-slate-700"
                }`}
              >
                <input
                  type="radio"
                  value="USER_DEVICE"
                  className="sr-only"
                  {...register("client_type")}
                />
                <Laptop className="h-4 w-4 text-blue-600 shrink-0" />
                <div>
                  <div>Developer PC</div>
                  <div className="text-[10px] font-normal text-slate-500">
                    Máy cá nhân dev
                  </div>
                </div>
              </label>

              <label
                className={`flex items-center gap-2.5 p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                  selectedType === "APP_SERVER"
                    ? "border-purple-600 bg-purple-50/50 text-purple-900 font-semibold"
                    : "border-slate-200 hover:bg-slate-50 text-slate-700"
                }`}
              >
                <input
                  type="radio"
                  value="APP_SERVER"
                  className="sr-only"
                  {...register("client_type")}
                />
                <Server className="h-4 w-4 text-purple-600 shrink-0" />
                <div>
                  <div>Workload Server</div>
                  <div className="text-[10px] font-normal text-slate-500">
                    Máy chủ / Docker
                  </div>
                </div>
              </label>
            </div>
            {errors.client_type && (
              <p className="text-[11px] text-rose-600 font-medium">
                {errors.client_type.message}
              </p>
            )}
          </div>

          {/* Validity Days */}
          <div className="space-y-1.5">
            <Label htmlFor="validity-days" className="text-xs font-semibold text-slate-700">
              Thời hạn chứng chỉ
            </Label>
            <NativeSelect
              id="validity-days"
              {...register("validity_days", { valueAsNumber: true })}
            >
              <option value={30}>30 ngày (Tiêu chuẩn bảo mật cao)</option>
              <option value={90}>90 ngày (1 Quý làm việc)</option>
              <option value={365}>365 ngày (1 Năm - Máy chủ dài hạn)</option>
            </NativeSelect>
            {errors.validity_days && (
              <p className="text-[11px] text-rose-600 font-medium">
                {errors.validity_days.message}
              </p>
            )}
          </div>

          <DialogFooter className="pt-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => handleOpenChange(false)}
              disabled={registerMutation.isPending}
              className="text-xs"
            >
              Hủy
            </Button>
            <Button
              type="submit"
              size="sm"
              disabled={registerMutation.isPending}
              className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium"
            >
              {registerMutation.isPending ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" />
                  Đang sinh cặp khóa...
                </>
              ) : (
                <>
                  <Plus className="h-3.5 w-3.5 mr-1" />
                  Khởi tạo chứng chỉ mTLS
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
