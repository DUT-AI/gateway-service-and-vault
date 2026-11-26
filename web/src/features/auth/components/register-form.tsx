"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRegisterMutation } from "../hooks/use-auth-queries";
import { registerSchema, type RegisterInput } from "../types";

export function RegisterForm() {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const registerMutation = useRegisterMutation();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterInput>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: RegisterInput) => {
    setErrorMessage(null);
    try {
      await registerMutation.mutateAsync(data);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } };
      setErrorMessage(
        e.response?.data?.detail ?? "Đăng ký thất bại. Email có thể đã tồn tại."
      );
    }
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="w-full max-w-sm space-y-4"
    >
      {errorMessage && (
        <div className="rounded-lg bg-red-100 p-3 text-sm text-red-700">
          {errorMessage}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Họ và tên
        </label>
        <input
          type="text"
          {...register("name")}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-[#042B5F] focus:outline-none focus:ring-[#042B5F]"
          placeholder="Nguyễn Văn A"
        />
        {errors.name && (
          <p className="mt-1 text-xs text-red-600">{errors.name.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Email</label>
        <input
          type="email"
          {...register("email")}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-[#042B5F] focus:outline-none focus:ring-[#042B5F]"
          placeholder="user@example.com"
        />
        {errors.email && (
          <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Mật khẩu
        </label>
        <input
          type="password"
          {...register("password")}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-[#042B5F] focus:outline-none focus:ring-[#042B5F]"
          placeholder="••••••••"
        />
        {errors.password && (
          <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting || registerMutation.isPending}
        className="flex w-full cursor-pointer justify-center rounded-md border border-transparent bg-[#042B5F] px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-[#031F46] focus:outline-none focus:ring-2 focus:ring-[#042B5F] focus:ring-offset-2 disabled:opacity-50"
      >
        {isSubmitting || registerMutation.isPending
          ? "Đang đăng ký..."
          : "Đăng ký"}
      </button>

      <p className="text-center text-sm text-gray-600">
        Đã có tài khoản?{" "}
        <Link
          href="/login"
          className="font-medium text-[#042B5F] hover:text-[#042B5F]"
        >
          Đăng nhập
        </Link>
      </p>
    </form>
  );
}
