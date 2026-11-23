import type { Schema } from "@/types/api";

export * from "./form-schemas";

export type VirtualKey = Schema<"VirtualKeySummaryResponse">;
export type GenerateKeyInput = Schema<"GenerateVirtualKeyRequest">;
export type GenerateKeyResult = Schema<"GenerateVirtualKeyResponse">;

export type VirtualKeyStatus = "ACTIVE" | "REVOKED";

export interface GenerateKeyModalState {
  isOpen: boolean;
  step: "FORM" | "RESULT";
  result?: GenerateKeyResult;
}
