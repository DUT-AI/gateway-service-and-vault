import { api } from "@/lib/api";
import type {
  BindServiceInput,
  Project,
  ProjectAllowedService,
  ProjectCreatePayload,
  UpdateQuotaInput,
} from "../types";

export const projectService = {
  async listProjects(): Promise<Project[]> {
    const { data } = await api.get<Project[]>("/gateway/projects");
    return data;
  },

  async getProjectById(projectId: string): Promise<Project> {
    const { data } = await api.get<Project>(`/gateway/projects/${projectId}`);
    return data;
  },

  async createProject(payload: ProjectCreatePayload): Promise<Project> {
    const { data } = await api.post<Project>("/gateway/projects", payload);
    return data;
  },

  async listAllowedServices(projectId: string): Promise<ProjectAllowedService[]> {
    const { data } = await api.get<ProjectAllowedService[]>(
      `/gateway/projects/${projectId}/services`
    );
    return data;
  },

  async bindService(
    projectId: string,
    payload: BindServiceInput
  ): Promise<ProjectAllowedService> {
    const { data } = await api.post<ProjectAllowedService>(
      `/gateway/projects/${projectId}/services`,
      payload
    );
    return data;
  },

  async updateServiceQuota(
    projectId: string,
    serviceId: string,
    payload: UpdateQuotaInput
  ): Promise<ProjectAllowedService> {
    const { data } = await api.put<ProjectAllowedService>(
      `/gateway/projects/${projectId}/services/${serviceId}/quota`,
      payload
    );
    return data;
  },

  async unbindService(projectId: string, serviceId: string): Promise<void> {
    await api.delete(`/gateway/projects/${projectId}/services/${serviceId}`);
  },
};
