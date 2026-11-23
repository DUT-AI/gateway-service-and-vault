---
description: "Task list for Web Phase 5 - Upstream Services Management & System Polish (DoD)"
---

# Tasks: Web Phase 5 - Upstream Services Management & System Polish (DoD)

**Input**: Design documents from `specs/011-web-upstream-services/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/services-api.md`, `quickstart.md`)  
**Prerequisites**: Phases 1 through 4 completed. OpenAPI schemas defined in `web/src/types/api.generated.d.ts`.  
**Organization**: Tasks are grouped into sequential Setup, Foundational, and User Story phases (P1 → P2 → P3) to enable independent implementation and testing.

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Maps to user stories from `spec.md` (`[US1]`, `[US2]`, `[US3]`)
- Exact file paths included in all descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature package structures and schema-derived TypeScript domain contracts for `services`.

- [X] T001 [P] Create feature directory structure for `web/src/features/services/` (`types/`, `services/`, `hooks/`, `components/`)
- [X] T002 [P] Define upstream service domain types deriving from `Schema<"UpstreamServiceResponse">` and `Schema<"UpstreamServiceCreateRequest">` in `web/src/features/services/types/index.ts`
- [X] T003 [P] Implement Zod form schemas quoting constraints verbatim (name min 2, max 100; slug min 2, max 100, regex `^[a-z0-9-]+$`; base_url regex `^https?://.+` with trailing slash stripping; auth_type enum `BEARER_TOKEN | API_KEY | BASIC_AUTH | NO_AUTH`; credential min 1; timeout_seconds min 1, max 300) and Vietnamese diacritic-stripping auto-slug utility in `web/src/features/services/types/form-schemas.ts`
- [X] T004 [P] Implement API service wrapper `upstreamService` (`listServices`, `createService`) calling `/api/v1/gateway/services` in `web/src/features/services/services/upstream-service.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core TanStack Query data fetching and mutation hooks required across user stories.

**⚠️ CRITICAL**: Must be completed before User Story UI components are integrated.

- [X] T005 [P] Implement TanStack Query hooks `useServicesQuery` (query key `["gateway", "services"]`) and `useCreateServiceMutation` with cache invalidation in `web/src/features/services/hooks/use-services-queries.ts`

**Checkpoint**: Foundation ready - Client-side state and networking hooks ready for UI integration.

---

## Phase 3: User Story 1 - Upstream Services Directory (Priority: P1) 🎯 MVP

**Goal**: Provide a dedicated management directory at `/services` displaying all registered upstream partner services, their routing slug, base URL, authentication type, timeout, and real-time search filtering.

**Independent Test**: Navigate to `/services` via AppShell navigation -> Verify data table renders service rows with Name, Slug badge, Base URL (with link & copy action), Auth Type badge (`Bearer Token`, `API Key`, `Basic Auth`, `No Auth`), Timeout in seconds, and Active status. Use search filter to find services in real time.

### Implementation for User Story 1

- [X] T006 [US1] Implement `ServicesTable` component rendering columns: Tên & Slug, Base URL (with external link and copy action), Loại xác thực (Auth Type badge), Thời gian chờ (Timeout), and Trạng thái, with real-time search and auth type filter pills in `web/src/features/services/components/services-table.tsx`
- [X] T007 [US1] Implement empty state and skeleton loading states inside `ServicesTable` when query is loading or zero services exist in `web/src/features/services/components/services-table.tsx`
- [X] T008 [US1] Export `ServicesTable` and service types in `web/src/features/services/components/index.ts` and `web/src/features/services/index.ts`
- [X] T009 [US1] Create the protected page route with breadcrumbs, page header, and `ServicesTable` container in `web/src/app/(protected)/services/page.tsx`

**Checkpoint**: At this point, User Story 1 (MVP) is fully functional and testable independently at `/services`.

---

## Phase 4: User Story 2 - Upstream Service Declaration & Credential Vaulting (Priority: P2)

**Goal**: Enable security administrators to declare new upstream services with Vietnamese auto-slug generation, URL normalization, auth method selection, and masked credential input encrypted at rest with AES-256-GCM.

**Independent Test**: On `/services`, click "Khai báo dịch vụ mới" -> Enter "Cổng Thanh Toán VNPay" -> Verify slug auto-populates `cong-thanh-toan-vnpay` -> Enter valid Base URL `https://sandbox.vnpayment.vn` -> Select `API_KEY` -> Enter Credential with Eye/EyeOff toggle -> Set Timeout 30s -> Submit -> Verify success toast, modal closes, credential is wiped from memory, and new service appears in table.

### Implementation for User Story 2

- [X] T010 [US2] Implement `CreateServiceDialog` component using Base/Radix UI Dialog with React Hook Form, Zod validation, auto-slug syncing, masked credential input (Eye/EyeOff visibility toggle), and timeout selection in `web/src/features/services/components/create-service-dialog.tsx`
- [X] T011 [US2] Integrate `CreateServiceDialog` into `ServicesTable` toolbar action button ("Khai báo dịch vụ mới") with Sonner toast feedback in `web/src/features/services/components/services-table.tsx`
- [X] T012 [US2] Re-export `CreateServiceDialog` in `web/src/features/services/components/index.ts` and `web/src/features/services/index.ts`

**Checkpoint**: User Stories 1 AND 2 are both functional. Upstream services can be cataloged, searched, and registered with encrypted credentials.

---

## Phase 5: User Story 3 - System Polish, Cross-Navigation & DoD Quality Gate (Priority: P3)

**Goal**: Verify cohesive navigation across all 5 platform modules, uniform responsive styling, active link state highlights, and pass all strict automated quality gates.

**Independent Test**: Navigate through `/dashboard` -> `/projects` -> `/projects/[id]` -> `/clients` -> `/services` -> Verify active sidebar item highlights correctly -> Verify `pnpm --prefix web typecheck`, `pnpm --prefix web build`, and `uv run pytest` pass cleanly with zero errors.

### Implementation for User Story 3

- [X] T013 [P] [US3] Verify and polish active navigation highlights in `web/src/components/layout/app-shell.tsx` for `/services`
- [X] T014 [P] [US3] Verify strict TypeScript compilation with zero errors via `pnpm --prefix web typecheck`
- [X] T015 [P] [US3] Verify Next.js production build succeeds with zero errors via `pnpm --prefix web build`
- [X] T016 [P] [US3] Verify backend pytest test suite remains 100% passing (46/46) via `uv run pytest`
- [X] T017 [US3] Execute interactive verification matching all scenarios in `specs/011-web-upstream-services/quickstart.md`

---

## Phase 6: Polish & Roadmap Closure

**Purpose**: Finalize documentation and update Web Roadmap to reflect complete delivery of all 5 phases.

- [X] T018 Update `docs/WEB_ROADMAP.md` to mark Phase 5 and the entire Web Roadmap as 100% completed

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (T001 - T004)
       │
       ▼
Phase 2: Foundational (T005)
       │
       ▼
Phase 3: User Story 1 (P1 MVP) (T006 - T009)
       │
       ▼
Phase 4: User Story 2 (P2) (T010 - T012)
       │
       ▼
Phase 5: User Story 3 (P3 DoD) (T013 - T017)
       │
       ▼
Phase 6: Polish & Roadmap Closure (T018)
```

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational (Phase 2). Can be deployed immediately as MVP.
- **User Story 2 (P2)**: Integrates into User Story 1 table view to enable service declaration.
- **User Story 3 (P3)**: Validates all 5 modules together as the Definition of Done.

---

## Parallel Execution Examples

### Setup & Foundational (Phases 1 & 2)
```bash
# Parallel execution for types and services:
Task T002: Define domain types in web/src/features/services/types/index.ts
Task T003: Implement form-schemas.ts
Task T004: Implement upstream-service.ts
Task T005: Implement use-services-queries.ts
```

### Verification Tasks (Phase 5)
```bash
# Parallel verification commands:
Task T014: pnpm --prefix web typecheck
Task T015: pnpm --prefix web build
Task T016: uv run pytest
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1: Setup (`T001` - `T004`).
2. Complete Phase 2: Foundational (`T005`).
3. Complete Phase 3: User Story 1 (`T006` - `T009`).
4. **STOP & VALIDATE**: Test `/services` directory independently.

### Incremental Delivery
1. Add Phase 4 (User Story 2: Declaration Dialog & Credential Vaulting) -> Test service registration.
2. Complete Phase 5 (User Story 3: System Polish & DoD Quality Gate) -> Run all automated gates.
3. Complete Phase 6 (Roadmap Closure) -> Update `docs/WEB_ROADMAP.md`.
