import { api } from "@/lib/api";
import type { Client } from "@/features/clients";
import type { VirtualKey, GenerateKeyInput, GenerateKeyResult } from "../types";

export const keyService = {
  async listProjectKeys(projectId: string): Promise<VirtualKey[]> {
    const { data } = await api.get<VirtualKey[]>(
      `/gateway/projects/${projectId}/keys`
    );
    return data;
  },

  async listProjectAvailableClients(projectId: string): Promise<Client[]> {
    const { data } = await api.get<Client[]>(
      `/gateway/projects/${projectId}/available-clients`
    );
    return data;
  },

  async generateVirtualKey(
    payload: GenerateKeyInput
  ): Promise<GenerateKeyResult> {
    const { data } = await api.post<GenerateKeyResult>("/gateway/keys", payload);
    return data;
  },

  async revokeVirtualKey(
    keyId: string
  ): Promise<{ message: string; [key: string]: string }> {
    const { data } = await api.post<{ message: string; [key: string]: string }>(
      `/gateway/keys/${keyId}/revoke`
    );
    return data;
  },
};
