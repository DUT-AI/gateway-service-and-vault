import { api } from "@/lib/api";
import type {
  CreateSecretPayload,
  CreateSecretsBatchPayload,
  GetSecretsResponse,
  GrantKeyPermissionPayload,
  IdentityPermissionsResponse,
  KeyPermission,
  Scope,
  SecretResponse,
} from "../types";

export const vaultService = {
  async listScopes(projectId: string): Promise<Scope[]> {
    const { data } = await api.get<Scope[]>(
      `/vault/projects/${projectId}/scopes`
    );
    return data;
  },

  async getSecrets(
    projectId: string,
    scope?: string,
    key?: string
  ): Promise<GetSecretsResponse> {
    const params: Record<string, string> = {};
    if (scope && scope !== "ALL") params.scope = scope;
    if (key) params.key = key;

    const { data } = await api.get<GetSecretsResponse>(
      `/vault/projects/${projectId}/secrets`,
      { params }
    );
    return data;
  },

  async createSecret(
    projectId: string,
    payload: CreateSecretPayload
  ): Promise<SecretResponse> {
    const { data } = await api.post<SecretResponse>(
      `/vault/projects/${projectId}/secrets`,
      payload
    );
    return data;
  },

  async createSecretsBatch(
    projectId: string,
    payload: CreateSecretsBatchPayload
  ): Promise<SecretResponse[]> {
    const { data } = await api.post<SecretResponse[]>(
      `/vault/projects/${projectId}/secrets/batch`,
      payload
    );
    return data;
  },

  async listPermissions(
    projectId: string,
    identityId: string
  ): Promise<IdentityPermissionsResponse> {
    const { data } = await api.get<IdentityPermissionsResponse>(
      `/vault/projects/${projectId}/permissions`,
      { params: { identity_id: identityId } }
    );
    return data;
  },

  async grantPermission(
    projectId: string,
    payload: GrantKeyPermissionPayload
  ): Promise<KeyPermission> {
    const { data } = await api.post<KeyPermission>(
      `/vault/projects/${projectId}/permissions`,
      payload
    );
    return data;
  },

  async revokePermission(
    projectId: string,
    identityId: string,
    secretKey: string
  ): Promise<void> {
    await api.delete(`/vault/projects/${projectId}/permissions`, {
      params: { identity_id: identityId, secret_key: secretKey },
    });
  },
};
