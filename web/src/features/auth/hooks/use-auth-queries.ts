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
    retry: false,
    staleTime: 5 * 60 * 1000,
  });
}

export function useLoginMutation() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: LoginInput) => authService.login(data),
    onSuccess: async () => {
      const user = await authService.getMe();
      queryClient.setQueryData(AUTH_QUERY_KEY, user);
      router.push("/dashboard");
    },
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
