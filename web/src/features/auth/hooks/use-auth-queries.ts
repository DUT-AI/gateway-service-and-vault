"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { authService } from "../services/auth-service";
import { SSO_LOGOUT_REDIRECT_URL } from "@/lib/auth-urls";
import type { LoginInput, RegisterInput } from "../types";

export const AUTH_QUERY_KEY = ["auth", "me"] as const;

export function useUserQuery() {
  return useQuery({
    queryKey: AUTH_QUERY_KEY,
    queryFn: () => authService.getMe(),
    retry: (failureCount, error: unknown) => {
      // Không retry nếu là 401 (chưa đăng nhập / hết hạn)
      const err = error as { response?: { status?: number } };
      if (err?.response?.status === 401) {
        return false;
      }
      return failureCount < 2;
    },
    staleTime: 5 * 60 * 1000,
    // Chỉ kích hoạt query khi không ở các trang public auth để tránh 401 loop
    enabled:
      typeof window === "undefined" ||
      (window.location.pathname !== "/login" &&
        window.location.pathname !== "/register"),
  });
}

function handleLoginSuccess(
  queryClient: ReturnType<typeof useQueryClient>,
  router: ReturnType<typeof useRouter>
) {
  queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY });
  const redirectUrl =
    typeof window !== "undefined"
      ? new URLSearchParams(window.location.search).get("redirect") ||
        "/dashboard"
      : "/dashboard";

  if (typeof window !== "undefined") {
    window.location.assign(redirectUrl);
  } else {
    router.push(redirectUrl);
  }
}

export function useLoginMutation() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: LoginInput) => authService.login(data),
    onSuccess: () => handleLoginSuccess(queryClient, router),
  });
}

export function useLoginSsoMutation() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: LoginInput) => authService.loginSso(data),
    onSuccess: () => handleLoginSuccess(queryClient, router),
  });
}

export function useRegisterMutation() {
  const router = useRouter();

  return useMutation({
    mutationFn: (data: RegisterInput) => authService.register(data),
    onSuccess: () => {
      router.push("/login");
    },
  });
}

function leaveSession(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.setQueryData(AUTH_QUERY_KEY, null);
  window.location.assign(SSO_LOGOUT_REDIRECT_URL);
}

export function useLogoutMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      await authService.logout();
    },
    onSuccess: () => leaveSession(queryClient),
    onError: () => leaveSession(queryClient),
  });
}
