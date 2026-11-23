import type { Schema } from "@/types/api";

export { createServiceSchema, type CreateServiceFormData } from "./form-schemas";

export type UpstreamService = Schema<"UpstreamServiceResponse">;
export type UpstreamServiceCreateInput = Schema<"UpstreamServiceCreateRequest">;

export type AuthType = "BEARER_TOKEN" | "API_KEY" | "BASIC_AUTH" | "NO_AUTH";

export interface ServiceFilterState {
  searchQuery: string;
  authTypeFilter: "ALL" | AuthType;
}
