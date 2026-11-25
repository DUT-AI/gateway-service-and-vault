"use client";

import { createContext, useContext, useMemo, useCallback } from "react";
import {
  type AuthContextValue,
  type LoginInput,
  type RegisterInput,
  type RoleTier,
  useLoginMutation,
  useLogoutMutation,
  useRegisterMutation,
  useUserQuery,
} from "@/features/auth";
import { redirectToInternalLogin } from "@/lib/auth-urls";

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
        (r: string) => r.toLowerCase() === role.toLowerCase()
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

  const roleTier = useMemo<RoleTier>(() => {
    if (!user) return "OTHER";
    const roles = new Set<string>();
    if (user.role) roles.add(user.role.trim().toLowerCase());
    if (Array.isArray(user.role_names)) {
      user.role_names.forEach((r) => {
        if (r) roles.add(r.trim().toLowerCase());
      });
    }
    const perms = new Set<string>(user.permissions ?? []);

    if (
      roles.has("admin") ||
      roles.has("system") ||
      roles.has("superuser") ||
      perms.has("*")
    ) {
      return "ADMIN";
    }
    if (roles.has("project developer") || roles.has("project_developer")) {
      return "PROJECT_DEVELOPER";
    }
    return "OTHER";
  }, [user]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user: user ?? null,
      isLoading,
      error: (error as Error) ?? null,
      roleTier,
      isAdmin: roleTier === "ADMIN",
      isDeveloper: roleTier === "PROJECT_DEVELOPER",
      isOtherRole: roleTier === "OTHER",
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
        redirectToInternalLogin();
      },
      refetchUser: () => {
        refetch();
      },
    }),
    [
      user,
      isLoading,
      error,
      roleTier,
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
