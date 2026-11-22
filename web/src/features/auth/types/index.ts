import { z } from "zod";
import type { Schema } from "@/types/api";

export const loginSchema = z.object({
  email: z
    .string()
    .min(1, "Vui lòng nhập địa chỉ email")
    .email("Định dạng email không hợp lệ"),
  password: z.string().min(1, "Vui lòng nhập mật khẩu"),
});
export type LoginInput = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
  name: z.string().min(1, "Vui lòng nhập họ tên"),
  email: z
    .string()
    .min(1, "Vui lòng nhập địa chỉ email")
    .email("Định dạng email không hợp lệ"),
  password: z.string().min(6, "Mật khẩu tối thiểu 6 ký tự"),
});
export type RegisterInput = z.infer<typeof registerSchema>;

export type User = Schema<"UserResponse">;
export type LoginPayload = Schema<"UserLoginRequest">;
export type RegisterPayload = Schema<"UserRegisterRequest">;
export type TokenResponse = Schema<"TokenResponse">;

export type AuthContextValue = {
  user: User | null;
  isLoading: boolean;
  error: Error | null;
  hasRole: (role: string) => boolean;
  hasPermission: (permission: string) => boolean;
  login: (data: LoginInput) => Promise<void>;
  register: (data: RegisterInput) => Promise<void>;
  logout: () => void;
  redirectToLogin: () => void;
  refetchUser: () => void;
};
