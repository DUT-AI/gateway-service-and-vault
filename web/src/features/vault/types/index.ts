import type { Schema } from "@/types/api";

export * from "./form-schemas";
export * from "./stream-types";

export type Scope = Schema<"ScopeResponse">;
export type GetSecretsResponse = Schema<"GetSecretsResponse">;
export type CreateSecretPayload = Schema<"CreateSecretRequest">;
export type SecretResponse = Schema<"SecretResponse">;
export type KeyPermission = Schema<"KeyPermissionResponse">;
export type GrantKeyPermissionPayload = Schema<"GrantKeyPermissionRequest">;
export type IdentityPermissionsResponse = Schema<"IdentityPermissionsResponse">;
export type UserOption = Schema<"UserOptionResponse">;

export interface FlatSecretItem {
  id: string; // `${scope_name}:${key}`
  scope_name: string;
  key: string;
  value: string;
}

export interface KeyPermissionItem {
  key: string;
  scope_name: string;
  isPermitted: boolean;
  isLoading?: boolean;
}
