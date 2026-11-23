import { api } from "@/lib/api";
import type { UpstreamService, UpstreamServiceCreateInput } from "../types";

export const upstreamService = {
  async listServices(): Promise<UpstreamService[]> {
    const { data } = await api.get<UpstreamService[]>("/gateway/services");
    return data;
  },

  async createService(
    payload: UpstreamServiceCreateInput
  ): Promise<UpstreamService> {
    const { data } = await api.post<UpstreamService>(
      "/gateway/services",
      payload
    );
    return data;
  },
};
