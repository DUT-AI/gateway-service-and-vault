"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { memberService, type AddProjectMemberPayload } from "../services/member-service";

export const MEMBER_KEYS = {
  list: (projectId: string) => ["projects", projectId, "members"] as const,
};

export function useProjectMembersQuery(projectId: string, enabled = true) {
  return useQuery({
    queryKey: MEMBER_KEYS.list(projectId),
    queryFn: () => memberService.listMembers(projectId),
    enabled: Boolean(projectId) && enabled,
    staleTime: 30 * 1000,
  });
}

export function useAddProjectMemberMutation(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AddProjectMemberPayload) =>
      memberService.addMember(projectId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MEMBER_KEYS.list(projectId) });
    },
  });
}

export function useRemoveProjectMemberMutation(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: number) => memberService.removeMember(projectId, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MEMBER_KEYS.list(projectId) });
    },
  });
}
