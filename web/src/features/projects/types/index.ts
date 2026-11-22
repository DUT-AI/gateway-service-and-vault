import type React from "react";
import type { Schema } from "@/types/api";

export * from "./form-schemas";

export type Project = Schema<"ProjectResponse">;
export type ProjectCreatePayload = Schema<"ProjectCreateRequest">;

export type WorkspaceTabKey = "vault" | "keys" | "settings";

export interface WorkspaceTab {
  key: WorkspaceTabKey;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badgeCount?: number;
}
