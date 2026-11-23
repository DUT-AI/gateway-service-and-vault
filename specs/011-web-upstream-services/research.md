# Research & Technical Decisions: Web Phase 5 - Upstream Services Management & System Polish (DoD)

**Feature Branch**: `011-web-upstream-services`  
**Date**: 2026-11-23  
**Status**: Completed  

---

## 1. Upstream Credential Protection & Zero-Client-Retention

### Decision
Raw upstream credentials (e.g., OpenAI API tokens, Payment Gateway API keys) are treated as transient write-only payloads in the frontend:
1. The user inputs the credential in a password-masked field with an Eye/EyeOff visibility toggle.
2. The credential is sent directly to `POST /api/v1/gateway/services`.
3. The backend encrypts the credential using `AES-256-GCM` before database persistence.
4. The response schema (`UpstreamServiceResponse`) intentionally omits the credential field entirely.
5. Upon form submission or dialog dismissal, React state and React Hook Form memory are cleared immediately.

### Rationale
- Enforces Constitution Principle VIII: Downstream clients and browser sessions never hold or view plaintext vendor secrets after initial registration.
- APISIX Gateway retrieves the decrypted credential internally at runtime and injects it into forwarded upstream requests via the `proxy-rewrite` plugin.

---

## 2. Vietnamese Diacritic Stripping & Auto-Slug Generation

### Decision
Implement automatic slug synchronization from the Service Name field using the existing URL-safe slug generator:
```typescript
export function generateSlug(input: string): string {
  return input
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // remove diacritics
    .replace(/[đĐ]/g, "d")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/[\s_]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 100);
}
```
If the user manually edits the slug input field, automatic syncing is disabled for that session.

### Rationale
- Ensures consistent kebab-case identifiers (e.g., "Cổng Thanh Toán VNPay" -> `cong-thanh-toan-vnpay`) required for routing rules in APISIX.

---

## 3. Upstream Authentication Methods & Protocol Mapping

### Decision
Support 4 standard upstream authentication types:
1. `BEARER_TOKEN` (Default): Injected as `Authorization: Bearer <credential>`
2. `API_KEY`: Injected as `X-API-Key: <credential>`
3. `BASIC_AUTH`: Injected as `Authorization: Basic <base64>`
4. `NO_AUTH`: Forwarded without credentials

### Rationale
- Covers >95% of third-party enterprise APIs (AI models, payment processors, cloud webhooks) while maintaining simple dropdown configuration.

---

## 4. Base URL Validation & Normalization

### Decision
Validate Base URLs using a strict Zod regex:
```typescript
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
  }, "Base URL không hợp lệ")
  .transform((url) => url.replace(/\/+$/, "")), // strip trailing slashes
```

### Rationale
- Stripping trailing slashes avoids double-slash routing bugs when the gateway appends subpaths (e.g. `https://api.openai.com/v1/` + `/chat/completions`).

---

## 5. System Architecture & Definition of Done (DoD)

### Decision
The Web application is organized around clean feature-based packaging:
- `web/src/features/services/`:
  - `types/`: Domain models derived from `Schema<"UpstreamServiceResponse">` and `Schema<"UpstreamServiceCreateRequest">`.
  - `services/upstream-service.ts`: API wrapper.
  - `hooks/use-services-queries.ts`: TanStack Query hooks.
  - `components/services-table.tsx`: Data table with search, badges, skeleton loading, and empty state.
  - `components/create-service-dialog.tsx`: Declaration modal with auto-slug and credential masking.
  - `index.ts`: Barrel export.
- `web/src/app/(protected)/services/page.tsx`: Protected route mapped to AppShell.

### DoD Validation:
- All 5 modules in `docs/WEB_ROADMAP.md` are operational.
- Strict type safety (`tsc --noEmit`).
- Production build succeeds (`next build`).
- Pytest suite 100% passing (46/46).
