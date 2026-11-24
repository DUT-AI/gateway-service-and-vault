import { api } from "@/lib/api";
import { clearAuthToken, setAuthToken } from "@/lib/auth-token";
import type { LoginPayload, TokenResponse, User } from "../types";

export const authService = {
  /**
   * Authenticate against central DUT-AI SSO IdP.
   */
  async login(payload: LoginPayload): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>("/auth/sso-login", payload);
    if (data.access_token) {
      setAuthToken(data.access_token);
      if (typeof document !== "undefined") {
        document.cookie = `access_token=${data.access_token}; path=/; SameSite=Lax`;
      }
    }
    return data;
  },

  /**
   * Alias for SSO authentication to maintain backward compatibility.
   */
  async loginSso(payload: LoginPayload): Promise<TokenResponse> {
    return this.login(payload);
  },

  /**
   * Local registration is deprecated under Pure SSO.
   */
  async register(..._args: unknown[]): Promise<User> {
    void _args;
    throw new Error(
      "Đăng ký tài khoản nội bộ đã ngừng hoạt động. Vui lòng đăng ký qua DUT-AI Manage IdP."
    );
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
