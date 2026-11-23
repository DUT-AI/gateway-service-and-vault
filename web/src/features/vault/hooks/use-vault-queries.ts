"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { vaultService } from "../services/vault-service";
import type { CreateSecretPayload, FlatSecretItem } from "../types";

export const VAULT_KEYS = {
  all: ["vault"] as const,
  scopes: (projectId: string) =>
    [...VAULT_KEYS.all, "scopes", projectId] as const,
  secrets: (projectId: string, scope?: string, key?: string) =>
    [...VAULT_KEYS.all, "secrets", projectId, { scope, key }] as const,
};

export function useScopesQuery(projectId: string) {
  return useQuery({
    queryKey: VAULT_KEYS.scopes(projectId),
    queryFn: () => vaultService.listScopes(projectId),
    enabled: Boolean(projectId),
    staleTime: 60 * 1000,
  });
}

export function useSecretsQuery(
  projectId: string,
  scope?: string,
  key?: string
) {
  return useQuery({
    queryKey: VAULT_KEYS.secrets(projectId, scope, key),
    queryFn: async () => {
      const response = await vaultService.getSecrets(projectId, scope, key);
      const flatItems: FlatSecretItem[] = [];

      if (response?.scopes) {
        Object.entries(response.scopes).forEach(([scopeName, secretsMap]) => {
          Object.entries(secretsMap).forEach(([secretKey, secretVal]) => {
            flatItems.push({
              id: `${scopeName}:${secretKey}`,
              scope_name: scopeName,
              key: secretKey,
              value: secretVal,
            });
          });
        });
      }

      return {
        ...response,
        flatItems,
      };
    },
    enabled: Boolean(projectId),
    staleTime: 30 * 1000,
  });
}

export function useSaveSecretMutation(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateSecretPayload) =>
      vaultService.createSecret(projectId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [...VAULT_KEYS.all, "scopes", projectId],
      });
      queryClient.invalidateQueries({
        queryKey: [...VAULT_KEYS.all, "secrets", projectId],
      });
    },
  });
}
