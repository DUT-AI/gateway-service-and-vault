# Research: Web Phase 2 - Dynamic Vault Management & Key-Level ACL

**Feature**: `008-web-vault-acl`  
**Date**: 2026-11-23  

## 1. Secret Value Security & Masking Pattern

### Decision
Store revealed/masked state purely in client component memory using a `Set<string>` of revealed secret keys (`revealedKeys`). By default, all secret values are rendered as bullet masks (`••••••••••••`) using a monospace font (`font-mono`).

### Rationale
- **Zero Accidental Exposure**: Observers or screen sharing sessions will not see sensitive values (API tokens, database passwords) without deliberate user unmasking.
- **Granular Control**: Users can unmask a single secret row at a time instead of exposing the entire vault.
- **Zero Leakage**: Values are masked purely in CSS/JSX presentation without modifying the underlying decrypted data string, ensuring copy-to-clipboard functionality copies the true value instantly.

### Alternatives Considered
- *Native `<input type="password">`*: Clunky in table cell displays, has browser-native password manager prompts and auto-fill conflicts.
- *Server-side masked endpoints*: Would require roundtrips to fetch individual plaintext values on each reveal click, adding latency and complexity.

---

## 2. Secrets Data Aggregation & Scope Filtering

### Decision
The backend endpoint `GET /api/v1/vault/projects/{id}/secrets` returns:
```json
{
  "project_id": "01JD27M508E9D0V2V1Z9Q1ABC0",
  "scopes": {
    "Common": {
      "APP_ENV": "production",
      "LOG_LEVEL": "info"
    },
    "Database": {
      "DB_HOST": "postgres.internal",
      "DB_PORT": "5432"
    }
  }
}
```
The frontend data layer transforms this nested object into a normalized flat array:
```typescript
export interface FlatSecretItem {
  id: string; // `${scopeName}:${key}`
  scope_name: string;
  key: string;
  value: string;
}
```

### Rationale
- Enables standard sorting, searching (by key or scope), and pagination across the table.
- Allows seamless switching between "Tất cả" (All Scopes) and individual scope tabs ("Common", "Database") with zero additional network requests.
- Preserves full reactivity: updating a secret automatically updates the table and scope tab badges.

---

## 3. Secret Key Format & Form Validation

### Decision
Secret keys are validated with Zod against upper snake_case:
```typescript
export const secretKeyRegex = /^[A-Z0-9_]+$/;

export const createSecretSchema = z.object({
  scope_name: z
    .string()
    .min(1, "Vui lòng chọn hoặc nhập nhóm Scope")
    .max(50, "Tên scope tối đa 50 ký tự")
    .regex(/^[a-zA-Z0-9_\s-]+$/, "Tên scope không hợp lệ"),
  key: z
    .string()
    .min(2, "Tên key tối thiểu 2 ký tự")
    .max(100, "Tên key tối đa 100 ký tự")
    .regex(secretKeyRegex, "Tên key phải viết hoa (ví dụ: DATABASE_URL, STRIPE_KEY)"),
  value: z.string().min(1, "Vui lòng nhập giá trị biến môi trường"),
});
```

### Rationale
- Matches standard POSIX environment variable naming conventions (`DATABASE_URL`, `JWT_SECRET`).
- Prevents invalid environment names that cause runtime crashes in containerized applications or SDKs (`dut-vault-sdk`).

---

## 4. Key-Level Permission Matrix & Optimistic Toggling

### Decision
The `KeyPermissionMatrixModal` combines:
1. Central user directory: `GET /api/v1/users/options` providing user options (`id: number`, `name`, `email`, `avatar_url`).
2. Current identity permissions: `GET /api/v1/vault/projects/{id}/permissions?identity_id={user_id}` returning `permitted_keys: string[]`.
3. Checkbox toggling:
   - When checked: `POST /api/v1/vault/projects/{id}/permissions` with `{ identity_id: String(user_id), identity_type: "user", secret_key: key }`.
   - When unchecked: `DELETE /api/v1/vault/projects/{id}/permissions?identity_id={user_id}&secret_key={key}`.
   - Optimistic UI updates ensure the checkbox toggles immediately with a subtle loading indicator.

### Rationale
- Enforces Principle V & VI of the Constitution: Native integer user IDs used across layers, converted to string for HTTP query param requirements.
- Provides immediate feedback to administrators when granting or revoking access to multiple keys without needing a tedious multi-step modal cycle.
