---
description: "Task list for Web Phase 4 - mTLS Device Management & Virtual Keys (Zero-Trust Gatekeeper)"
---

# Tasks: Web Phase 4 - mTLS Device Management & Virtual Keys (Zero-Trust Gatekeeper)

**Input**: Design documents from `specs/010-web-mtls-virtual-keys/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/clients-keys-api.md`, `quickstart.md`)  
**Prerequisites**: Phase 1, Phase 2, and Phase 3 completed. OpenAPI schemas defined in `web/src/types/api.generated.d.ts`.  
**Organization**: Tasks are grouped into sequential Setup, Foundational, and User Story phases (P1 → P2 → P3) to enable independent implementation and testing.

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Maps to user stories from `spec.md` (`[US1]`, `[US2]`, `[US3]`)
- Exact file paths included in all descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature package structures and schema-derived TypeScript domain contracts for `clients` and `keys`.

- [X] T001 [P] Create feature directory structure for `web/src/features/clients/` (`types/`, `services/`, `hooks/`, `components/`, `utils/`) and `web/src/features/keys/` (`types/`, `services/`, `hooks/`, `components/`)
- [X] T002 [P] Define client domain types deriving from `Schema<"ClientSummaryResponse">`, `Schema<"RegisterClientRequest">`, and `Schema<"RegisterClientResponse">` in `web/src/features/clients/types/index.ts`
- [X] T003 [P] Define virtual key domain types deriving from `Schema<"VirtualKeySummaryResponse">`, `Schema<"GenerateVirtualKeyRequest">`, and `Schema<"GenerateVirtualKeyResponse">` in `web/src/features/keys/types/index.ts`
- [X] T004 [P] Implement API service wrapper for clients (`listClients`, `registerClient`) calling `/api/v1/gateway/clients` in `web/src/features/clients/services/client-service.ts`
- [X] T005 [P] Implement API service wrapper for virtual keys (`listProjectKeys`, `generateVirtualKey`, `revokeVirtualKey`) calling `/api/v1/gateway/keys` and `/api/v1/gateway/projects/{id}/keys` in `web/src/features/keys/services/key-service.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core client-side download utility and TanStack Query state hooks required across user stories.

**⚠️ CRITICAL**: Must be completed before User Story UI components are integrated.

- [X] T006 [P] Implement zero-persistence file download helper using native `Blob` and `URL.createObjectURL` with MIME types (`application/x-x509-ca-cert`, `application/pkcs8`, `text/plain`) in `web/src/features/clients/utils/download-file.ts`
- [X] T007 [P] Implement TanStack Query hooks `useClientsQuery` (query key `["gateway", "clients"]`) and `useRegisterClientMutation` with cache invalidation in `web/src/features/clients/hooks/use-clients-queries.ts`
- [X] T008 [P] Implement TanStack Query hooks `useProjectKeysQuery` (query key `["projects", projectId, "keys"]`), `useGenerateKeyMutation`, and `useRevokeKeyMutation` in `web/src/features/keys/hooks/use-keys-queries.ts`

**Checkpoint**: Foundation ready - Client-side state and networking hooks ready for UI integration.

---

## Phase 3: User Story 1 - mTLS Client & Device Directory (Priority: P1) 🎯 MVP

**Goal**: Provide a dedicated directory at `/clients` displaying all registered developer machines and server workloads, their SHA-256 certificate fingerprints, serial numbers, validity status, and real-time filtering.

**Independent Test**: Navigate to `/clients` via AppShell navigation -> Verify data table renders device records with name, type badge (`Developer PC` / `Workload Server`), truncated fingerprint with copy trigger, expiration date, and active/revoked status badge. Filter by name or fingerprint to verify real-time search.

### Implementation for User Story 1

- [X] T009 [US1] Implement `ClientsTable` component rendering columns: Tên thiết bị, Loại client (`Developer PC` for `USER_DEVICE`, `Workload Server` for `APP_SERVER`), Fingerprint SHA-256 (`font-mono text-xs` with copy button), Hạn chứng chỉ, Trạng thái hoạt động, and search filter input in `web/src/features/clients/components/clients-table.tsx`
- [X] T010 [US1] Implement empty state and skeleton loading states inside `ClientsTable` when query is loading or zero devices exist in `web/src/features/clients/components/clients-table.tsx`
- [X] T011 [US1] Export `ClientsTable` and client types in `web/src/features/clients/index.ts`
- [X] T012 [US1] Create the protected page route with breadcrumbs, page header, and `ClientsTable` container in `web/src/app/(protected)/clients/page.tsx`

**Checkpoint**: At this point, User Story 1 (MVP) is fully functional and testable independently at `/clients`.

---

## Phase 4: User Story 2 - Device Registration & One-Time Certificate Download (Priority: P2)

**Goal**: Enable developers and operators to register a new workstation or server via modal dialog and immediately download `client.crt` and `client.key` with strict zero-persistence security guardrails.

**Independent Test**: On `/clients`, click "Đăng ký thiết bị mới" -> Fill device name, select type (`USER_DEVICE` or `APP_SERVER`), select validity period (`30`, `90`, `365` days) -> Submit -> Modal transitions to `CertDownloadDialog` -> Click "Tải client.crt" and "Tải client.key" -> Verify files download cleanly to local disk -> Close modal -> Verify private key is purged from memory and new device appears in the table.

### Implementation for User Story 2

- [X] T013 [US2] Implement `RegisterClientDialog` component using Base/Radix UI Dialog with Zod schema validation (quoting constraints verbatim: name min 2, max 64, regex `^[a-zA-Z0-9\s._-]+$`, client_type enum `USER_DEVICE | APP_SERVER`, validity_days enum `30 | 90 | 365`) in `web/src/features/clients/components/register-client-dialog.tsx`
- [X] T014 [US2] Implement `CertDownloadDialog` component displaying certificate serial, SHA-256 fingerprint, amber one-time warning alert, and download buttons ("Tải client.crt", "Tải client.key", "Tải cả hai tệp") in `web/src/features/clients/components/cert-download-dialog.tsx`
- [X] T015 [US2] Integrate `RegisterClientDialog` and `CertDownloadDialog` into `ClientsTable` header action button ("Đăng ký thiết bị mới") with toast notifications in `web/src/features/clients/components/clients-table.tsx`
- [X] T016 [US2] Update feature barrel exports in `web/src/features/clients/index.ts`

**Checkpoint**: User Stories 1 AND 2 are both functional. Device registration and X.509 certificate distribution are complete.

---

## Phase 5: User Story 3 - Project Virtual Keys Management & Instant Revocation (Priority: P3)

**Goal**: Issue project-scoped Virtual Access Keys bound 1:1 to registered devices, show one-time raw key tokens with ready-to-run CLI commands, and allow instant key revocation with confirmation.

**Independent Test**: Open `/projects/[id]` -> Click "Virtual Keys" tab -> Click "Cấp Virtual Key mới" -> Select registered device -> Submit -> Verify raw key `vkey_dev_...` displays in amber security alert alongside copy button and CLI command `dut-vault run --key=vkey_dev_... -- python main.py` -> Click complete -> Verify key row displays `ACTIVE` status in `VirtualKeysTable` -> Click "Thu hồi" -> Confirm dialog -> Verify status switches immediately to `REVOKED` (rose badge).

### Implementation for User Story 3

- [X] T017 [US3] Implement `VirtualKeysTable` component displaying columns: Key Prefix (`vkey_dev_...`), Thiết bị client ràng buộc (device name & badge), Thời điểm cấp, Trạng thái (`ACTIVE` emerald vs `REVOKED` rose), and "Thu hồi" (Revoke) action button in `web/src/features/keys/components/virtual-keys-table.tsx`
- [X] T018 [US3] Implement `GenerateKeyModal` with two-step workflow: Step 1 (device selector dropdown filtering active non-revoked clients via `useClientsQuery`), Step 2 (one-time secret view with copy button, amber warning, and pre-formatted CLI execution snippet `dut-vault run --key=<KEY> -- python main.py`) in `web/src/features/keys/components/generate-key-modal.tsx`
- [X] T019 [US3] Implement revocation confirmation dialog triggering `useRevokeKeyMutation`, updating key row status to `REVOKED`, and showing Sonner toast in `web/src/features/keys/components/virtual-keys-table.tsx`
- [X] T020 [US3] Implement `VirtualKeysView` container component orchestrating header, action buttons, `GenerateKeyModal`, and `VirtualKeysTable` in `web/src/features/keys/components/virtual-keys-view.tsx`
- [X] T021 [US3] Export `VirtualKeysView` and virtual key types in `web/src/features/keys/index.ts`
- [X] T022 [US3] Mount `<VirtualKeysView projectId={project.id} />` into the "Virtual Keys" tab of `web/src/features/projects/components/project-workspace-tabs.tsx` replacing previous placeholder

**Checkpoint**: All three user stories (Directory, Device Registration, Virtual Keys) are fully integrated.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Type safety verification, production build check, end-to-end automated sanity testing, and documentation alignment.

- [X] T023 [P] Verify strict TypeScript compilation with zero errors via `pnpm --prefix web typecheck`
- [X] T024 [P] Verify Next.js production build succeeds with zero errors via `pnpm --prefix web build`
- [X] T025 [P] Verify existing backend pytest test suite remains 100% passing (46/46) via `uv run pytest`
- [X] T026 Execute end-to-end sanity verification matching all 4 scenarios in `specs/010-web-mtls-virtual-keys/quickstart.md`
- [X] T027 Update `docs/WEB_ROADMAP.md` to reflect Phase 4 completion status

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (T001 - T005)
       │
       ▼
Phase 2: Foundational (T006 - T008)
       │
       ├───────────────────────────────────────┐
       ▼                                       ▼
Phase 3: User Story 1 (P1 MVP)       Phase 5: User Story 3 (P3)
       (T009 - T012)                           (T017 - T022)
       │                                       ▲
       ▼                                       │ (Requires clients hook)
Phase 4: User Story 2 (P2) ───────────────────┘
       (T013 - T016)
       │
       ▼
Phase 6: Polish & Cross-Cutting Concerns (T023 - T027)
```

### User Story Dependencies

- **User Story 1 (P1)**: Depends only on Foundational (Phase 2). Can be deployed immediately as MVP.
- **User Story 2 (P2)**: Extends User Story 1 with registration dialog and certificate downloading.
- **User Story 3 (P3)**: Depends on Foundational (Phase 2) and `useClientsQuery` from Phase 2/3 to populate the client device dropdown during key generation.

---

## Parallel Execution Examples

### Setup & Foundational (Phases 1 & 2)
```bash
# Parallel execution for types and services:
Task T002: Define client domain types in web/src/features/clients/types/index.ts
Task T003: Define virtual key domain types in web/src/features/keys/types/index.ts
Task T004: Implement client-service.ts
Task T005: Implement key-service.ts
Task T006: Implement download-file.ts helper
Task T007: Implement use-clients-queries.ts
Task T008: Implement use-keys-queries.ts
```

### Verification Tasks (Phase 6)
```bash
# Parallel verification commands:
Task T023: pnpm --prefix web typecheck
Task T024: pnpm --prefix web build
Task T025: uv run pytest
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1: Setup (`T001` - `T005`).
2. Complete Phase 2: Foundational (`T006` - `T008`).
3. Complete Phase 3: User Story 1 (`T009` - `T012`).
4. **STOP & VALIDATE**: Test `/clients` directory independently.

### Incremental Delivery
1. Add Phase 4 (User Story 2: Device Registration & Cert Download) -> Test `client.crt` and `client.key` downloads independently.
2. Add Phase 5 (User Story 3: Virtual Keys & Revocation) -> Test `/projects/[id]` Virtual Keys tab and APISIX key lifecycle.
3. Complete Phase 6 (Polish & Verification) -> Run all automated gates.
