import { api } from "@/lib/api";
import type { UserOption } from "../types";

export const userDirectoryService = {
  async listUserOptions(): Promise<UserOption[]> {
    const { data } = await api.get<UserOption[]>("/users/options");
    return data;
  },
};
