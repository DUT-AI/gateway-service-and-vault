import { api } from "@/lib/api";
import type { Project, ProjectCreatePayload } from "../types";

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
};
