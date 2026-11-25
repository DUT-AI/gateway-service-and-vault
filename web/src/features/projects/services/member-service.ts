import { api } from "@/lib/api";
import type { Schema } from "@/types/api";

export type ProjectMember = Schema<"ProjectMemberResponse">;
export type AddProjectMemberPayload = Schema<"ProjectMemberCreateRequest">;

export const memberService = {
  async listMembers(projectId: string): Promise<ProjectMember[]> {
    const { data } = await api.get<ProjectMember[]>(
      `/gateway/projects/${projectId}/members`
    );
    return data;
  },

  async addMember(
    projectId: string,
    payload: AddProjectMemberPayload
  ): Promise<ProjectMember[]> {
    const { data } = await api.post<ProjectMember[]>(
      `/gateway/projects/${projectId}/members`,
      payload
    );
    return data;
  },

  async removeMember(projectId: string, userId: number): Promise<void> {
    await api.delete(`/gateway/projects/${projectId}/members/${userId}`);
  },
};
