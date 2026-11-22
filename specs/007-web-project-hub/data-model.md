# Data Model: Web Phase 1 - Project Hub & Core Navigation

**Feature**: `007-web-project-hub`  
**Date**: 2026-11-23  

## 1. Frontend Entities & Schema Mapping

All frontend entities are derived directly from the OpenAPI schema types generated in `web/src/types/api.generated.d.ts` using the `Schema<T>` helper from `web/src/types/api.ts`.

### Project Entity
Represents a project workspace boundary retrieved from `GET /api/v1/gateway/projects`.

```typescript
import type { Schema } from "@/types/api";

export type Project = Schema<"ProjectResponse">;
```

**Attributes:**
- `id`: `string` (ULID string, e.g. `01JD27M508E9D0V2V1Z9Q1ABC0`)
- `name`: `string` (2-100 characters, human-readable name, e.g. "Payment Gateway Core")
- `slug`: `string` (2-100 characters, URL-safe identifier, e.g. "payment-gateway-core")
- `description`: `string | null` (optional markdown or plain-text summary)
- `created_at`: `string` (ISO 8601 UTC timestamp, e.g. "2026-11-23T04:20:00Z")

---

### Project Creation Form Input
Zod-validated form model for `CreateProjectDialog`.

```typescript
export const createProjectSchema = z.object({
  name: z
    .string()
    .min(2, "Tên dự án tối thiểu 2 ký tự")
    .max(100, "Tên dự án tối đa 100 ký tự"),
  slug: z
    .string()
    .min(2, "Mã slug tối thiểu 2 ký tự")
    .max(100, "Mã slug tối đa 100 ký tự")
    .regex(/^[a-z0-9-]+$/, "Slug chỉ được chứa chữ thường, số và dấu gạch ngang (-)"),
  description: z.string().max(500, "Mô tả tối đa 500 ký tự").optional(),
});

export type CreateProjectInput = z.infer<typeof createProjectSchema>;
export type ProjectCreatePayload = Schema<"ProjectCreateRequest">;
```

---

### Workspace Sub-Navigation State
Represents active tab selection on `/projects/[id]`.

```typescript
export type WorkspaceTabKey = "vault" | "keys" | "settings";

export interface WorkspaceTab {
  key: WorkspaceTabKey;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badgeCount?: number;
}
```

---

### AppShell Navigation Item Entity
Represents an item on the global sidebar.

```typescript
export interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  activePrefix?: string;
  badge?: string;
}
```

---

## 2. Validation & Invariants

1. **Slug Invariant**: Slugs must be lower-case alphanumeric with hyphens only (`^[a-z0-9-]+$`). No spaces, uppercase letters, or special characters permitted.
2. **Type Purity**: Form inputs match `ProjectCreateRequest` payload without data loss or unexpected property coercion.
3. **Null Safety**: `description` can be `null` or `undefined`; UI must display fallback text (e.g., "Chưa có mô tả") when empty.
