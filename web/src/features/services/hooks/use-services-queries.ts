import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { upstreamService } from "../services/upstream-service";
import type { UpstreamService, UpstreamServiceCreateInput } from "../types";

export const SERVICES_QUERY_KEY = ["gateway", "services"] as const;

export function useServicesQuery() {
  return useQuery<UpstreamService[], Error>({
    queryKey: SERVICES_QUERY_KEY,
    queryFn: () => upstreamService.listServices(),
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function useCreateServiceMutation() {
  const queryClient = useQueryClient();

  return useMutation<UpstreamService, Error, UpstreamServiceCreateInput>({
    mutationFn: (payload: UpstreamServiceCreateInput) =>
      upstreamService.createService(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SERVICES_QUERY_KEY });
    },
  });
}
