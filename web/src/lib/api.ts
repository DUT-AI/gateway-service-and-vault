import axios from "axios";
import { clearAuthToken, getAuthToken } from "./auth-token";
import { redirectToInternalLogin } from "./auth-urls";

export const api = axios.create({
  baseURL:
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const isLoginRequest = error.config?.url?.includes("/auth/login");
      const isAlreadyOnAuthPage =
        typeof window !== "undefined" &&
        (window.location.pathname === "/login" ||
          window.location.pathname === "/register");

      if (
        !isLoginRequest &&
        !isAlreadyOnAuthPage &&
        typeof window !== "undefined"
      ) {
        clearAuthToken();
        redirectToInternalLogin();
      }
    }
    return Promise.reject(error);
  }
);
