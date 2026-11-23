"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { vaultService } from "../services/vault-service";
import type { GrantKeyPermissionPayload } from "../types";

export const PERMISSION_KEYS = {
  all: ["vault", "permissions"] as const,
  list: (projectId: string, identityId: string) =>
    [...PERMISSION_KEYS.all, projectId, identityId] as const,
};

export function useIdentityPermissionsQuery(
  projectId: string,
  identityId?: string
) {
  return useQuery({
    queryKey: PERMISSION_KEYS.list(projectId, identityId || ""),
    queryFn: () => vaultService.listPermissions(projectId, identityId || ""),
    enabled: Boolean(projectId && identityId),
    staleTime: 30 * 1000,
  });
}

export function useGrantPermissionMutation(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: GrantKeyPermissionPayload) =>
      vaultService.grantPermission(projectId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: PERMISSION_KEYS.list(projectId, variables.identity_id),
      });
    },
  });
}

export function useRevokePermissionMutation(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      identityId,
      secretKey,
    }: {
      identityId: string;
      secretKey: string;
    }) => vaultService.revokePermission(projectId, identityId, secretKey),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: PERMISSION_KEYS.list(projectId, variables.identityId),
      });
    },
  });
}
