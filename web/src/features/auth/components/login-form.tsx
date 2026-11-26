"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  AlertCircle,
  Eye,
  EyeOff,
  Info,
  Loader2,
  Lock,
  Mail,
  ShieldCheck,
} from "lucide-react";
import { useLoginMutation } from "../hooks/use-auth-queries";
import { loginSchema, type LoginInput } from "../types";

export function LoginForm() {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const loginMutation = useLoginMutation();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: LoginInput) => {
    setErrorMessage(null);
    try {
      await loginMutation.mutateAsync(data);
    } catch (err: unknown) {
      console.error("[SSO Login] Error:", err);
      const e = err as {
        response?: {
          status?: number;
          data?: { detail?: string; message?: string };
        };
        message?: string;
      };

      if (e.response?.data?.detail) {
        setErrorMessage(e.response.data.detail);
      } else if (e.response?.data?.message) {
        setErrorMessage(e.response.data.message);
      } else if (e.response?.status === 401) {
        setErrorMessage(
          "Email hoặc mật khẩu SSO không chính xác. Vui lòng kiểm tra lại thông tin tài khoản DUT-AI của bạn."
        );
      } else if (e.response?.status === 502 || e.response?.status === 504) {
        setErrorMessage(
          "Máy chủ trung tâm DUT-AI phản hồi quá lâu hoặc đang bảo trì. Vui lòng thử lại sau giây lát."
        );
      } else if (e.message === "Network Error" || !e.response) {
        setErrorMessage(
          "Không thể kết nối tới máy chủ API Gateway. Vui lòng kiểm tra kết nối mạng và đảm bảo Gateway đang hoạt động."
        );
      } else {
        setErrorMessage(
          e.message ??
            "Xác thực SSO thất bại. Vui lòng kiểm tra lại email hoặc mật khẩu DUT-AI của bạn."
        );
      }
    }
  };

  const isLoading = isSubmitting || loginMutation.isPending;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="w-full space-y-4">
      {errorMessage && (
        <div className="flex items-start gap-2.5 rounded-lg border border-red-200 bg-red-50 p-3.5 text-sm text-red-700">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Email tài khoản DUT-AI
        </label>
        <div className="relative mt-1">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <Mail className="h-4 w-4 text-gray-400" />
          </div>
          <input
            type="email"
            autoComplete="username"
            disabled={isLoading}
            {...register("email")}
            className="block w-full rounded-lg border border-slate-300 py-2.5 pl-9 pr-3 text-sm text-slate-900 shadow-2xs placeholder:text-slate-400 focus:border-[#042B5F] focus:outline-none focus:ring-2 focus:ring-[#042B5F]/15 disabled:bg-slate-50 disabled:text-slate-500"
            placeholder="user@dutai.io.vn"
          />
        </div>
        {errors.email && (
          <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
        )}
      </div>

      <div>
        <div className="flex items-center justify-between">
          <label className="block text-sm font-medium text-gray-700">
            Mật khẩu SSO
          </label>
        </div>
        <div className="relative mt-1">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <Lock className="h-4 w-4 text-gray-400" />
          </div>
          <input
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            disabled={isLoading}
            {...register("password")}
            className="block w-full rounded-lg border border-slate-300 py-2.5 pl-9 pr-10 text-sm text-slate-900 shadow-2xs placeholder:text-slate-400 focus:border-[#042B5F] focus:outline-none focus:ring-2 focus:ring-[#042B5F]/15 disabled:bg-slate-50 disabled:text-slate-500"
            placeholder="••••••••"
          />
          <button
            type="button"
            onClick={() => setShowPassword((prev) => !prev)}
            tabIndex={-1}
            className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
          >
            {showPassword ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
          </button>
        </div>
        {errors.password && (
          <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>
        )}
      </div>

      <div className="pt-2">
        <button
          type="submit"
          disabled={isLoading}
          className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#042B5F] px-4 py-2.5 text-sm font-semibold text-white shadow-xs transition-all hover:bg-[#031F46] focus:outline-none focus:ring-2 focus:ring-[#042B5F] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin text-white" />
              <span>Đang xác thực SSO...</span>
            </>
          ) : (
            <>
              <ShieldCheck className="h-4 w-4 text-white" />
              <span>Đăng nhập SSO DUT-AI</span>
            </>
          )}
        </button>
      </div>

      <div className="mt-4 rounded-lg border border-[#042B5F]/15 bg-[#EEF3FA] p-3 text-xs text-[#042B5F]">
        <div className="flex items-start gap-2">
          <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[#042B5F]" />
          <p className="leading-relaxed">
            Hệ thống áp dụng <strong>DUT-AI Pure SSO</strong>. Tài khoản được cấp
            và quản lý tập trung từ hệ thống quản trị DUT-AI Workspace. Nếu bạn
            chưa có tài khoản hoặc quên mật khẩu, vui lòng liên hệ quản trị viên
            hệ thống.
          </p>
        </div>
      </div>
    </form>
  );
}
