import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clientService } from "../services/client-service";
import type { Client, RegisterClientInput, RegisterClientResult } from "../types";

export const CLIENTS_QUERY_KEY = ["gateway", "clients"] as const;

export function useClientsQuery() {
  return useQuery<Client[], Error>({
    queryKey: CLIENTS_QUERY_KEY,
    queryFn: () => clientService.listClients(),
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function useRegisterClientMutation() {
  const queryClient = useQueryClient();

  return useMutation<RegisterClientResult, Error, RegisterClientInput>({
    mutationFn: (payload: RegisterClientInput) =>
      clientService.registerClient(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: CLIENTS_QUERY_KEY });
    },
  });
}
