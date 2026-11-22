"use client";

import { createContext, useContext, useMemo, useCallback } from "react";
import {
  type AuthContextValue,
  type LoginInput,
  type RegisterInput,
  useLoginMutation,
  useLogoutMutation,
  useRegisterMutation,
  useUserQuery,
} from "@/features/auth";
import { redirectToSsoLogin } from "@/lib/auth-urls";

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: user, isLoading, error, refetch } = useUserQuery();
  const loginMutation = useLoginMutation();
  const registerMutation = useRegisterMutation();
  const logoutMutation = useLogoutMutation();

  const hasRole = useCallback(
    (role: string): boolean => {
      if (!user?.role_names) return false;
      return user.role_names.some(
        (r) => r.toLowerCase() === role.toLowerCase()
      );
    },
    [user]
  );

  const hasPermission = useCallback(
    (permission: string): boolean => {
      if (!user?.permissions) return false;
      return (
        user.permissions.includes("*") || user.permissions.includes(permission)
      );
    },
    [user]
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user: user ?? null,
      isLoading,
      error: (error as Error) ?? null,
      hasRole,
      hasPermission,
      login: async (data: LoginInput) => {
        await loginMutation.mutateAsync(data);
      },
      register: async (data: RegisterInput) => {
        await registerMutation.mutateAsync(data);
      },
      logout: () => {
        logoutMutation.mutate();
      },
      redirectToLogin: () => {
        redirectToSsoLogin();
      },
      refetchUser: () => {
        refetch();
      },
    }),
    [
      user,
      isLoading,
      error,
      hasRole,
      hasPermission,
      loginMutation,
      registerMutation,
      logoutMutation,
      refetch,
    ]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
