import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { Client } from "@/features/clients";
import { keyService } from "../services/key-service";
import type {
  VirtualKey,
  GenerateKeyInput,
  GenerateKeyResult,
} from "../types";

export const projectKeysQueryKey = (projectId: string) =>
  ["projects", projectId, "keys"] as const;

export const projectAvailableClientsQueryKey = (projectId: string) =>
  ["projects", projectId, "available-clients"] as const;

export function useProjectKeysQuery(projectId: string) {
  return useQuery<VirtualKey[], Error>({
    queryKey: projectKeysQueryKey(projectId),
    queryFn: () => keyService.listProjectKeys(projectId),
    enabled: Boolean(projectId),
    staleTime: 1000 * 30,
  });
}

export function useProjectAvailableClientsQuery(
  projectId: string,
  enabled = true
) {
  return useQuery<Client[], Error>({
    queryKey: projectAvailableClientsQueryKey(projectId),
    queryFn: () => keyService.listProjectAvailableClients(projectId),
    enabled: Boolean(projectId) && enabled,
    staleTime: 1000 * 30,
  });
}

export function useGenerateKeyMutation(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation<GenerateKeyResult, Error, GenerateKeyInput>({
    mutationFn: (payload: GenerateKeyInput) =>
      keyService.generateVirtualKey(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: projectKeysQueryKey(projectId),
      });
    },
  });
}

export function useRevokeKeyMutation(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation<{ message: string }, Error, string>({
    mutationFn: (keyId: string) => keyService.revokeVirtualKey(keyId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: projectKeysQueryKey(projectId),
      });
    },
  });
}
