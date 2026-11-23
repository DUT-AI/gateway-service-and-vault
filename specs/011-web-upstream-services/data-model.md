# Data Model: Web Phase 5 - Upstream Services Management & System Polish (DoD)

**Feature Branch**: `011-web-upstream-services`  
**Date**: 2026-11-23  
**Status**: Completed  

---

## 1. Domain Entities & Type Mappings

All frontend types strictly derive from the authoritative backend OpenAPI schemas via `Schema<T>` in `web/src/types/api.generated.d.ts`.

```
┌────────────────────────────────────────────────────────┐
│                    UpstreamService                     │
│         (3rd-Party Partner / API Integration)          │
├────────────────────────────────────────────────────────┤
│ id: string (UUID)                                      │
│ name: string                                           │
│ slug: string (kebab-case routing identifier)           │
│ base_url: string (HTTP/HTTPS endpoint)                 │
│ auth_type: BEARER_TOKEN | API_KEY | BASIC_AUTH | ...   │
│ timeout_seconds: number (e.g. 30)                      │
│ is_active: boolean                                     │
│ created_at: string (ISO 8601 UTC timestamp)            │
└────────────────────────────────────────────────────────┘
```

---

## 2. Upstream Service Models (`web/src/features/services/types/index.ts`)

### `UpstreamService` (Entity Model)
Represents a partner service whose endpoint and credentials are proxy-protected by APISIX Gateway.
- **Backend Schema**: `Schema<"UpstreamServiceResponse">`
- **Fields**:
  - `id`: `string` - Unique service UUID.
  - `name`: `string` - Display name (e.g. "OpenAI API Platform", "VNPay Payment Gateway").
  - `slug`: `string` - Kebab-case slug used for API Gateway route paths (e.g. `openai-api-platform`).
  - `base_url`: `string` - Upstream target base URL (e.g. `https://api.openai.com/v1`).
  - `auth_type`: `AuthType` - Authentication mechanism (`"BEARER_TOKEN" | "API_KEY" | "BASIC_AUTH" | "NO_AUTH"`).
  - `timeout_seconds`: `number` - Request timeout limit (default: 30s).
  - `is_active`: `boolean` - Whether the service is currently enabled in the gateway.
  - `created_at`: `string` - Timestamp of creation.

### `UpstreamServiceCreateInput`
Payload sent when declaring a new upstream service.
- **Backend Schema**: `Schema<"UpstreamServiceCreateRequest">`
- **Fields**:
  - `name`: `string` - Required name (2–100 chars).
  - `slug`: `string` - Required slug (2–100 chars, kebab-case).
  - `base_url`: `string` - Required HTTP/HTTPS URL.
  - `auth_type`: `string` - Defaults to `"BEARER_TOKEN"`.
  - `credential`: `string` - Raw upstream API key / secret (Write-Only; encrypted at rest with AES-256-GCM).
  - `timeout_seconds`: `number` - Defaults to 30.

---

## 3. UI View Models & State Transitions

### Lifecycle State Machine: Upstream Service
```
[POST /services] ──> ( ACTIVE / IS_ACTIVE=TRUE ) ──> ( INACTIVE / IS_ACTIVE=FALSE )
```

### UI View State Models

```typescript
export type AuthType = "BEARER_TOKEN" | "API_KEY" | "BASIC_AUTH" | "NO_AUTH";

export interface ServiceFilterState {
  searchQuery: string;
  authTypeFilter: "ALL" | AuthType;
}

export interface CreateServiceDialogState {
  isOpen: boolean;
}
```

---

## 4. Client-Side Validation Rules (Zod)

```typescript
import { z } from "zod";

export const createServiceSchema = z.object({
  name: z
    .string()
    .min(2, "Tên dịch vụ phải có ít nhất 2 ký tự")
    .max(100, "Tên dịch vụ không vượt quá 100 ký tự"),
  slug: z
    .string()
    .min(2, "Slug phải có ít nhất 2 ký tự")
    .max(100, "Slug không vượt quá 100 ký tự")
    .regex(/^[a-z0-9-]+$/, "Slug chỉ được chứa chữ thường, số và dấu gạch ngang (-)"),
  base_url: z
    .string()
    .min(1, "Vui lòng nhập Base URL")
    .regex(/^https?:\/\/.+/, "Base URL phải bắt đầu bằng http:// hoặc https://")
    .refine((url) => {
      try {
        new URL(url);
        return true;
      } catch {
        return false;
      }
    }, "Base URL không đúng định dạng URL hợp lệ"),
  auth_type: z.enum(["BEARER_TOKEN", "API_KEY", "BASIC_AUTH", "NO_AUTH"], {
    message: "Vui lòng chọn phương thức xác thực hợp lệ",
  }),
  credential: z.string().min(1, "Vui lòng nhập Token hoặc Credential đối tác"),
  timeout_seconds: z.coerce
    .number()
    .int("Timeout phải là số nguyên")
    .min(1, "Timeout tối thiểu 1 giây")
    .max(300, "Timeout tối đa 300 giây"),
});

export type CreateServiceFormData = z.infer<typeof createServiceSchema>;
```
