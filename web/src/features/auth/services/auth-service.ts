import { api } from "@/lib/api";
import { clearAuthToken, setAuthToken } from "@/lib/auth-token";
import type {
  LoginPayload,
  RegisterPayload,
  TokenResponse,
  User,
} from "../types";

export const authService = {
  async login(payload: LoginPayload): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>("/auth/login", payload);
    if (data.access_token) {
      setAuthToken(data.access_token);
      if (typeof document !== "undefined") {
        document.cookie = `access_token=${data.access_token}; path=/; SameSite=Lax`;
      }
    }
    return data;
  },

  async register(payload: RegisterPayload): Promise<User> {
    const { data } = await api.post<User>("/auth/register", payload);
    return data;
  },

  async getMe(): Promise<User> {
    const res = await fetch("/api/auth/me", {
      method: "GET",
      headers: { Accept: "application/json" },
      credentials: "include",
    });

    if (res.status === 401) {
      throw new Error("Phiên đăng nhập đã hết hạn hoặc chưa đăng nhập.");
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(
        err.detail ||
          `Máy chủ xác thực IdP đang bận (HTTP ${res.status}). Vui lòng thử lại sau.`
      );
    }

    return await res.json();
  },

  async logout(): Promise<void> {
    clearAuthToken();
    try {
      await fetch("/api/auth/logout", { method: "POST" });
    } catch (e) {
      console.error("Lỗi đăng xuất:", e);
    }
  },
};
