# Data Model: Web Phase 2 - Dynamic Vault Management & Key-Level ACL

**Feature**: `008-web-vault-acl`  
**Date**: 2026-11-23  

## 1. Frontend Entities & Schema Mapping

All frontend types are mapped directly from backend OpenAPI schemas via `Schema<T>` in `web/src/types/api.ts`.

### Schema Aliases

```typescript
import type { Schema } from "@/types/api";

export type Scope = Schema<"ScopeResponse">;
export type GetSecretsResponse = Schema<"GetSecretsResponse">;
export type CreateSecretPayload = Schema<"CreateSecretRequest">;
export type SecretResponse = Schema<"SecretResponse">;
export type KeyPermission = Schema<"KeyPermissionResponse">;
export type GrantKeyPermissionPayload = Schema<"GrantKeyPermissionRequest">;
export type IdentityPermissionsResponse = Schema<"IdentityPermissionsResponse">;
export type UserOption = Schema<"UserOptionResponse">;
```

---

### Normalized UI Entities

#### FlatSecretItem
A flattened representation of a key-value secret extracted from `GetSecretsResponse.scopes` for table rendering and search filtering.

```typescript
export interface FlatSecretItem {
  id: string; // Composite key: `${scope_name}:${key}`
  scope_name: string;
  key: string;
  value: string;
}
```

#### KeyPermissionItem
Represents the state of a single secret key inside the permission matrix.

```typescript
export interface KeyPermissionItem {
  key: string;
  scope_name: string;
  isPermitted: boolean;
  isLoading?: boolean;
}
```

---

## 2. Form Input Models (Zod Validation)

### CreateSecretInput
Validation schema for adding or updating an encrypted secret.

```typescript
export const secretKeyRegex = /^[A-Z0-9_]+$/;

export const createSecretSchema = z.object({
  scope_name: z
    .string()
    .min(1, "Vui lòng chọn hoặc nhập tên nhóm Scope")
    .max(50, "Tên scope tối đa 50 ký tự")
    .regex(/^[a-zA-Z0-9_\s-]+$/, "Tên scope không được chứa ký tự đặc biệt"),
  key: z
    .string()
    .min(2, "Tên key tối thiểu 2 ký tự")
    .max(100, "Tên key tối đa 100 ký tự")
    .regex(secretKeyRegex, "Tên key phải viết hoa (ví dụ: DATABASE_URL, STRIPE_KEY)"),
  value: z.string().min(1, "Vui lòng nhập giá trị biến môi trường"),
});

export type CreateSecretInput = z.infer<typeof createSecretSchema>;
```

---

## 3. State Machines & Transitions

### Secret Value Masking State

```
[Masked (••••••••••••)] ──(Click Eye Icon)──> [Revealed (Plaintext)]
          ▲                                           │
          └─────────────(Click EyeOff Icon)───────────┘
```

- Default state: Masked.
- Action: Unmasks only the active row.
- Invariant: Copy-to-clipboard always reads the decrypted plaintext value regardless of mask state.

### Key Permission Lifecycle

```
[Revoked (Unchecked)] ──(Check Box: POST /permissions)──> [Granted (Checked)]
          ▲                                                      │
          └────────(Uncheck Box: DELETE /permissions)────────────┘
```

- Toggling sends granular grant or revoke commands.
- Optimistic update updates UI checkbox immediately while awaiting network response.
- On error: rolls back checkbox and shows Sonner error toast.
