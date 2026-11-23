import type { Schema } from "@/types/api";

export * from "./form-schemas";

export type Client = Schema<"ClientSummaryResponse">;
export type RegisterClientInput = Schema<"RegisterClientRequest">;
export type RegisterClientResult = Schema<"RegisterClientResponse">;

export type ClientType = "USER_DEVICE" | "APP_SERVER";

export interface ClientFilterState {
  searchQuery: string;
  typeFilter: "ALL" | ClientType;
}
