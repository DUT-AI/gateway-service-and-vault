"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { projectService } from "../services/project-service";
import type {
  BindServiceInput,
  ProjectCreatePayload,
  UpdateQuotaInput,
} from "../types";

export const PROJECT_KEYS = {
  all: ["projects"] as const,
  lists: () => [...PROJECT_KEYS.all, "list"] as const,
  details: () => [...PROJECT_KEYS.all, "detail"] as const,
  detail: (id: string) => [...PROJECT_KEYS.details(), id] as const,
  allowedServices: (id: string) =>
    [...PROJECT_KEYS.detail(id), "allowed-services"] as const,
};

export function useProjectsQuery() {
  return useQuery({
    queryKey: PROJECT_KEYS.lists(),
    queryFn: () => projectService.listProjects(),
    staleTime: 60 * 1000,
  });
}

export function useProjectDetailQuery(projectId: string) {
  return useQuery({
    queryKey: PROJECT_KEYS.detail(projectId),
    queryFn: () => projectService.getProjectById(projectId),
    enabled: Boolean(projectId),
    staleTime: 60 * 1000,
    retry: (failureCount, error: any) => {
      if (error?.response?.status === 404) return false;
      return failureCount < 2;
    },
  });
}

export function useCreateProjectMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ProjectCreatePayload) =>
      projectService.createProject(payload),
    onSuccess: (newProject) => {
      queryClient.invalidateQueries({ queryKey: PROJECT_KEYS.lists() });
      queryClient.setQueryData(PROJECT_KEYS.detail(newProject.id), newProject);
    },
  });
}

export function useProjectAllowedServicesQuery(projectId: string) {
  return useQuery({
    queryKey: PROJECT_KEYS.allowedServices(projectId),
    queryFn: () => projectService.listAllowedServices(projectId),
    enabled: Boolean(projectId),
    staleTime: 30 * 1000,
  });
}

export function useBindServiceToProjectMutation(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: BindServiceInput) =>
      projectService.bindService(projectId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: PROJECT_KEYS.allowedServices(projectId),
      });
    },
  });
}

export function useUpdateServiceQuotaMutation(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      serviceId,
      payload,
    }: {
      serviceId: string;
      payload: UpdateQuotaInput;
    }) => projectService.updateServiceQuota(projectId, serviceId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: PROJECT_KEYS.allowedServices(projectId),
      });
    },
  });
}

export function useUnbindServiceFromProjectMutation(projectId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (serviceId: string) =>
      projectService.unbindService(projectId, serviceId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: PROJECT_KEYS.allowedServices(projectId),
      });
    },
  });
}
