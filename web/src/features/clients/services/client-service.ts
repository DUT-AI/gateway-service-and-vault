import { api } from "@/lib/api";
import type { Client, RegisterClientInput, RegisterClientResult } from "../types";

export const clientService = {
  async listClients(): Promise<Client[]> {
    const { data } = await api.get<Client[]>("/gateway/clients");
    return data;
  },

  async registerClient(
    payload: RegisterClientInput
  ): Promise<RegisterClientResult> {
    const { data } = await api.post<RegisterClientResult>(
      "/gateway/clients",
      payload
    );
    return data;
  },
};
