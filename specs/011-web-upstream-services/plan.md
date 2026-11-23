# Implementation Plan: Web Phase 5 - Upstream Services Management & System Polish (DoD)

**Branch**: `011-web-upstream-services` | **Date**: 2026-11-23 | **Spec**: [specs/011-web-upstream-services/spec.md](spec.md)

**Input**: Feature specification from `specs/011-web-upstream-services/spec.md`

---

## Summary

Deliver the complete Upstream Services Management and System Polish module (Web Phase 5 - Definition of Done), providing:
1. **Upstream Services Catalog (`/services`)**: A management directory for 3rd-party partner endpoints (OpenAI, Payment Gateways, ERP APIs, etc.) proxy-protected by APISIX Gateway, displaying their Name, Slug, Base URL, Auth Type, Timeout, and Active status.
2. **Upstream Service Declaration Modal (`CreateServiceDialog`)**: Secure form with automated Vietnamese diacritic-stripping kebab-case slug generation, URL validation, authentication protocol selection (`BEARER_TOKEN`, `API_KEY`, `BASIC_AUTH`, `NO_AUTH`), and masked credential vaulting.
3. **System-Wide UI Polish & Definition of Done (DoD)**: Seamless cross-module navigation across all 5 modules (Dashboard, Projects, Vault, Clients/mTLS, Services), uniform responsive design, Sonner toast feedback, and clean passes on TypeScript type checking, Next.js production build, and backend test suites.

---

## Technical Context

**Language/Version**: TypeScript 5.7+ (Frontend), Python 3.12+ (Backend)  
**Primary Dependencies**: Next.js 16 (App Router), React 19, Tailwind CSS v4, TanStack Query v5, Axios, Zod, React Hook Form, Lucide React, Sonner (Toasts)  
**Storage**: Ephemeral client-side state for write-only credentials; TanStack Query cache; PostgreSQL (Backend persistence)  
**Testing**: `pnpm --prefix web typecheck`, `pnpm --prefix web build`, `uv run pytest`  
**Target Platform**: Modern desktop & mobile browsers (Chrome, Firefox, Safari, Edge)  
**Project Type**: Monorepo Web Application (`web/`) communicating with FastAPI Gateway Service (`apps/api/`)  
**Performance Goals**: 
- Page load & table render < 200ms
- Upstream service declaration mutation < 500ms
- Real-time search filter update < 50ms  
**Constraints**: 
- Principle IV: Offline Contract & Type Synchronization (100% types derived from `web/src/types/api.generated.d.ts`)
- Principle V: Pure DUT-AI SSO, zero local passwords, strict integer IDs
- Principle VIII: Zero-Trust Identity Binding & Upstream Protection (upstream credentials encrypted at rest with AES-256-GCM and injected transparently by APISIX Gateway)
- Zero-Disk / Zero-Client-Retention for upstream credentials after modal submission.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Compliance Status |
|---|---|---|
| **I. Clean Architecture & Domain Purity** | Domain entities decoupled from transport | PASS: Backend entities in `modules/gateway/` remain pure dataclasses; frontend domain types isolate in `features/services/`. |
| **II. Modular Monolith with Dishka IoC** | Encapsulated bounded contexts | PASS: Gateway router injects `GatewayService` via Dishka; frontend feature encapsulates its own API client, hooks, and components. |
| **III. Transactional Outbox Pattern** | Asynchronous events use outbox | PASS: Service registration events sync to APISIX gateway without blocking request cycle. |
| **IV. Offline Contract & Type Sync** | Derived types from OpenAPI schema | PASS: All types mapped directly to `Schema<"UpstreamServiceResponse">` and `Schema<"UpstreamServiceCreateRequest">`. |
| **V. DUT-AI SSO & Pure Identity** | Native integer IDs, pure SSO | PASS: Session maintained via SSO tokens/cookies; no local user passwords stored. |
| **VI. Dynamic Vault Access Control** | Secrets encrypted at rest with AES-256-GCM | PASS: Upstream credentials encrypted with AES-256-GCM at backend; never exposed in plain text in queries. |
| **VIII. Zero-Trust Identity Binding & APISIX** | Upstream protection via credential injection | PASS: Gateway injects real upstream credentials into forwarded requests, shielding underlying service credentials from clients. |

---

## Project Structure

### Documentation (this feature)

```text
specs/011-web-upstream-services/
├── spec.md                  # Requirements, User Stories, and DoD Criteria
├── plan.md                  # This implementation plan
├── research.md              # Phase 0 technical decisions (AES-256-GCM, auto-slug, URL validation)
├── data-model.md            # Phase 1 data models & validation schemas
├── contracts/
│   └── services-api.md      # Phase 1 API contracts for /gateway/services
└── quickstart.md            # Phase 1 verification and quickstart instructions
```

### Source Code Layout

```text
web/src/
├── app/
│   └── (protected)/
│       └── services/
│           └── page.tsx                         # Dedicated Upstream Services Catalog page
├── features/
│   └── services/
│       ├── types/
│       │   ├── form-schemas.ts                  # Zod validation schema & Vietnamese slug generator
│       │   └── index.ts                         # Domain models derived from OpenAPI schemas
│       ├── services/
│       │   └── upstream-service.ts              # API client: listServices, createService
│       ├── hooks/
│       │   └── use-services-queries.ts          # TanStack Query: useServicesQuery, useCreateServiceMutation
│       ├── components/
│       │   ├── services-table.tsx               # Data table with filtering, auth badges, empty/loading states
│       │   ├── create-service-dialog.tsx        # Modal with auto-slug, URL check, and credential masking
│       │   └── index.ts                         # Component barrel exports
│       └── index.ts                             # Public feature barrel export
```

---

## Architecture & Component Breakdown

### 1. `upstream-service.ts`
- `listServices(): Promise<UpstreamService[]>` -> `GET /api/v1/gateway/services`
- `createService(input: UpstreamServiceCreateInput): Promise<UpstreamService>` -> `POST /api/v1/gateway/services`

### 2. `use-services-queries.ts`
- `useServicesQuery()`: TanStack Query hook with query key `["gateway", "services"]`.
- `useCreateServiceMutation()`: TanStack Mutation with cache invalidation for `["gateway", "services"]`.

### 3. `services-table.tsx`
- Columns:
  1. **Tên & Slug**: Service name with Server/Globe icon, along with a monospace slug badge (`bg-slate-100 text-slate-700`).
  2. **Base URL**: External target endpoint with external link indicator and copy button.
  3. **Loại xác thực**: Badge indicating auth method:
     - `BEARER_TOKEN`: Blue badge "Bearer Token"
     - `API_KEY`: Purple badge "API Key"
     - `BASIC_AUTH`: Amber badge "Basic Auth"
     - `NO_AUTH`: Slate badge "No Auth"
  4. **Timeout**: Formatted seconds (e.g. `30s`, `60s`).
  5. **Trạng thái**: Badge emerald "Đang hoạt động" (`is_active === true`) vs Badge rose "Tạm dừng".
- Search input for name, slug, or base URL.
- Auth Type filter pills (`Tất cả`, `Bearer Token`, `API Key`, `Basic Auth`, `No Auth`).
- "Khai báo dịch vụ mới" action button opening `CreateServiceDialog`.
- Skeleton rows and friendly empty state.

### 4. `create-service-dialog.tsx`
- Dialog powered by `@base-ui/react/dialog`.
- Form validation via React Hook Form + Zod (`createServiceSchema`):
  - **Tên dịch vụ**: Text input.
  - **Slug**: Auto-generated via `generateSlug(name)` unless manually edited.
  - **Base URL**: URL input validated for `http://` or `https://` format.
  - **Phương thức xác thực**: Select dropdown for `BEARER_TOKEN`, `API_KEY`, `BASIC_AUTH`, `NO_AUTH`.
  - **Thông tin xác thực (Credential)**: Password field with Eye/EyeOff toggle. Security helper text explaining AES-256-GCM encryption.
  - **Thời gian chờ (Timeout)**: Select dropdown for 5s, 15s, 30s, 60s, 120s.
- Pending spinner and automatic query invalidation upon success.

### 5. `web/src/app/(protected)/services/page.tsx`
- Protected page with breadcrumbs (`Trang chủ` / `Dịch vụ hệ thống`).
- Page header with title, subtitle, and Zero-Trust Reverse Proxy badge.
- Renders `<ServicesTable />`.

---

## Implementation Phases & Dependency Graph

```text
Phase 1: Setup & Domain Types
├── types/form-schemas.ts & types/index.ts
└── services/upstream-service.ts

Phase 2: Foundational Query Hooks
└── hooks/use-services-queries.ts

Phase 3: UI Components
├── create-service-dialog.tsx
├── services-table.tsx
├── index.ts
└── /services/page.tsx

Phase 4: Full System Verification & DoD Polish
├── TypeScript compilation (pnpm --prefix web typecheck)
├── Next.js production build (pnpm --prefix web build)
├── Backend pytest test suite (uv run pytest)
└── Documentation & Web Roadmap updates
```

---

## Risk Analysis & Mitigation

| Risk | Impact | Mitigation Strategy |
|---|---|---|
| Trailing slash in Base URL causing double-slash routing | Medium | Zod transform `.transform(url => url.replace(/\/+$/, ""))` strips trailing slashes before submit. |
| Credential leaked in browser console or network payload | High | Exclude credential field from response DTO; write-only form state reset upon modal close. |
| Duplicate slug conflict | Medium | Backend returns HTTP 400/422 if slug exists; form catches and displays clear toast error. |
