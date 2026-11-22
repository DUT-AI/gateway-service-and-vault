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

  async loginSso(payload: LoginPayload): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>("/auth/sso-login", payload);
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
    const { data } = await api.get<User>("/auth/me");
    return data;
  },

  async logout(): Promise<void> {
    clearAuthToken();
    try {
      await api.post("/auth/logout");
    } catch (e) {
      console.error("Lỗi đăng xuất:", e);
    }
  },
};
