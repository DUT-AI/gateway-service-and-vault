# Implementation Plan: Web Phase 4 - mTLS Device Management & Virtual Keys (Zero-Trust Gatekeeper)

**Branch**: `010-web-mtls-virtual-keys` | **Date**: 2026-11-23 | **Spec**: [specs/010-web-mtls-virtual-keys/spec.md](spec.md)

**Input**: Feature specification from `specs/010-web-mtls-virtual-keys/spec.md`

---

## Summary

Deliver the complete frontend Zero-Trust Gatekeeper administrative interface (Web Phase 4) comprising:
1. **mTLS Device Directory (`/clients`)**: An administrative inventory interface displaying all registered developer workstations and server workloads, their cryptographic SHA-256 fingerprints, serial numbers, validity windows, and active/revoked statuses.
2. **Device Registration & Certificate Issuance Modal**: Form allowing users to register new devices, select validity periods, and immediately download the issued private key (`client.key`) and public X.509 certificate (`client.crt`) with zero browser persistence.
3. **Project Virtual Keys Management (`/projects/[id]` -> Virtual Keys tab)**: In-workspace interface allowing operators to issue new Virtual Access Keys bound 1:1 to registered devices, view one-time raw key tokens with ready-to-run CLI commands, and perform instant zero-trust key revocations.

---

## Technical Context

**Language/Version**: TypeScript 5.7+ (Frontend), Python 3.12+ (Backend)  
**Primary Dependencies**: Next.js 16 (App Router), React 19, Tailwind CSS v4, TanStack Query v5, Axios, Zod, Lucide React, Sonner (Toasts)  
**Storage**: Ephemeral client-side state for one-time private keys and tokens; TanStack Query cache; PostgreSQL (Backend persistence)  
**Testing**: `pnpm --prefix web typecheck`, `pnpm --prefix web build`, `uv run pytest`  
**Target Platform**: Modern desktop & mobile browsers (Chrome, Firefox, Safari, Edge)  
**Project Type**: Monorepo Web Application (`web/`) communicating with FastAPI Gateway Service (`apps/api/`)  
**Performance Goals**: 
- Page load & table render < 200ms
- Modal transition & certificate generation < 1.5s
- Virtual key revocation roundtrip < 500ms
- File download trigger < 50ms (synchronous Blob dispatch)  
**Constraints**: 
- Principle IV: Offline Contract & Type Synchronization (100% types derived from `web/src/types/api.generated.d.ts`)
- Principle V: Pure DUT-AI SSO, zero local passwords, strict integer IDs
- Principle VIII: Zero-Trust Identity Binding (1:1 binding between client devices and virtual keys)
- Ephemeral security: Private key PEM and raw virtual key token are never saved to local/session storage and are discarded upon modal dismiss.  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Compliance Status |
|---|---|---|
| **I. Clean Architecture & Domain Purity** | Domain entities decouple from persistence/transport | PASS: Backend entities in `modules/gateway/` remain pure dataclasses; frontend domain types isolate in feature folders. |
| **II. Modular Monolith with Dishka IoC** | Modular encapsulation and DI scoping | PASS: Gateway routers inject `GatewayService` via Dishka; frontend features (`clients`, `keys`) encapsulate their own services, hooks, and components. |
| **III. Transactional Outbox Pattern** | Asynchronous operations use outbox | PASS: Key revocation triggers background synchronization events to Redis/APISIX without blocking. |
| **IV. Offline Contract & Type Sync** | No manual TypeScript interfaces for API payloads | PASS: All types mapped directly to `Schema<"ClientSummaryResponse">`, `Schema<"RegisterClientResponse">`, `Schema<"VirtualKeySummaryResponse">`, `Schema<"GenerateVirtualKeyResponse">`. |
| **V. DUT-AI SSO & Pure Identity** | Native integer IDs, zero local passwords | PASS: User identity derived from SSO; owner_id uses authenticated user identity. |
| **VI. Dynamic Vault Access Control** | Secrets encrypted at rest with AES-256-GCM | PASS: Vault keys continue to use granular permissions; Virtual Keys provide Zero-Trust network gatekeeping. |
| **VIII. Zero-Trust Identity Binding** | 1:1 binding between Virtual Key and mTLS cert | PASS: Primary goal of Phase 4; keys are strictly generated for a specific `client_id` and enforced by APISIX. |

---

## Project Structure

### Documentation (this feature)

```text
specs/010-web-mtls-virtual-keys/
├── spec.md                  # Requirements, User Stories, and Criteria
├── plan.md                  # This implementation plan
├── research.md              # Phase 0 decisions (Blob downloads, zero-retention, Zod validation)
├── data-model.md            # Phase 1 data models & state machine
├── contracts/
│   └── clients-keys-api.md  # Phase 1 API contracts for the 5 gateway endpoints
└── quickstart.md            # Phase 1 verification and quickstart instructions
```

### Source Code Layout

```text
web/src/
├── app/
│   └── (protected)/
│       ├── clients/
│       │   └── page.tsx                         # Dedicated mTLS Device Inventory page
│       └── projects/
│           └── [id]/
│               └── page.tsx                     # Project Workspace page
├── features/
│   ├── clients/
│   │   ├── types/
│   │   │   └── index.ts                         # Client domain types derived from OpenAPI schemas
│   │   ├── services/
│   │   │   └── client-service.ts                # API client: listClients, registerClient
│   │   ├── hooks/
│   │   │   └── use-clients-queries.ts           # TanStack Query: useClientsQuery, useRegisterClientMutation
│   │   ├── components/
│   │   │   ├── clients-table.tsx                # Data table with filtering, status badges, empty/loading states
│   │   │   ├── register-client-dialog.tsx       # Registration modal with Zod validation
│   │   │   └── cert-download-dialog.tsx         # Download view for client.crt and client.key
│   │   └── index.ts                             # Public feature barrel export
│   ├── keys/
│   │   ├── types/
│   │   │   └── index.ts                         # Virtual key domain types derived from OpenAPI schemas
│   │   ├── services/
│   │   │   └── key-service.ts                   # API client: listProjectKeys, generateVirtualKey, revokeVirtualKey
│   │   ├── hooks/
│   │   │   └── use-keys-queries.ts              # TanStack Query: useProjectKeysQuery, useGenerateKeyMutation, useRevokeKeyMutation
│   │   ├── components/
│   │   │   ├── virtual-keys-table.tsx           # Keys table with client binding, status, and revoke trigger
│   │   │   ├── generate-key-modal.tsx           # Two-step key creation modal & one-time CLI snippet
│   │   │   └── virtual-keys-view.tsx            # Integrated container tab for Project Workspace
│   │   └── index.ts                             # Public feature barrel export
│   └── projects/
│       └── components/
│           └── project-workspace-tabs.tsx       # Mounts VirtualKeysView into "Virtual Keys" tab
```

---

## Architecture & Component Breakdown

### 1. Feature: `clients` (`web/src/features/clients/`)

- **`client-service.ts`**:
  - `listClients(): Promise<Client[]>` -> `GET /api/v1/gateway/clients`
  - `registerClient(input: RegisterClientInput): Promise<RegisterClientResult>` -> `POST /api/v1/gateway/clients`
- **`use-clients-queries.ts`**:
  - `useClientsQuery()`: TanStack Query hook with query key `["gateway", "clients"]`.
  - `useRegisterClientMutation()`: TanStack Mutation with cache invalidation for `["gateway", "clients"]`.
- **`clients-table.tsx`**:
  - Displays columns: **Tên thiết bị**, **Loại**, **Fingerprint SHA-256**, **Hạn chứng chỉ**, **Trạng thái**.
  - Search filter input for device name or fingerprint substring.
  - Type badge: `Developer PC` (blue) for `USER_DEVICE`, `Workload Server` (purple) for `APP_SERVER`.
  - Fingerprint formatted with truncated monospace font (`3a:f1:...:88:31`) and copy-to-clipboard button.
- **`register-client-dialog.tsx`**:
  - Form dialog built with Base/Radix UI Dialog.
  - Fields: Name (min 2, max 64 chars), Client Type (`USER_DEVICE` or `APP_SERVER`), Validity Days (30, 90, 365 days).
  - On submit, calls `registerClientMutation.mutateAsync`. Upon success, transitions immediately to `cert-download-dialog.tsx`.
- **`cert-download-dialog.tsx`**:
  - Displays certificate serial and SHA-256 fingerprint.
  - Prominent amber security alert: *"Khóa riêng (Private Key) chỉ được tạo và hiển thị 1 lần duy nhất. Hãy lưu vào thư mục an toàn."*
  - Action buttons: "Tải client.crt", "Tải client.key", "Tải cả hai tệp".
  - Uses `triggerFileDownload(filename, content, mimeType)`.

### 2. Feature: `keys` (`web/src/features/keys/`)

- **`key-service.ts`**:
  - `listProjectKeys(projectId: string): Promise<VirtualKey[]>` -> `GET /api/v1/gateway/projects/{id}/keys`
  - `generateVirtualKey(input: GenerateKeyInput): Promise<GenerateKeyResult>` -> `POST /api/v1/gateway/keys`
  - `revokeVirtualKey(keyId: string): Promise<{ message: string }>` -> `POST /api/v1/gateway/keys/{id}/revoke`
- **`use-keys-queries.ts`**:
  - `useProjectKeysQuery(projectId: string)`: TanStack Query key `["projects", projectId, "keys"]`.
  - `useGenerateKeyMutation(projectId: string)`: Mutation invalidating `["projects", projectId, "keys"]`.
  - `useRevokeKeyMutation(projectId: string)`: Mutation invalidating `["projects", projectId, "keys"]`.
- **`virtual-keys-table.tsx`**:
  - Displays columns: **Key Prefix**, **Thiết bị ràng buộc (Client)**, **Thời điểm cấp**, **Trạng thái**, **Thao tác**.
  - Status badge: `ACTIVE` (emerald-100 text-emerald-800) vs `REVOKED` (rose-100 text-rose-800).
  - "Thu hồi" action button opening a confirmation prompt.
- **`generate-key-modal.tsx`**:
  - Step 1 (Selection): Client device selector dropdown populated from `useClientsQuery()`. Excludes/disables revoked devices.
  - Step 2 (Result): Displays full `vkey_dev_...` token, copy button, and CLI snippet:
    `dut-vault run --key=vkey_dev_... -- python main.py`
- **`virtual-keys-view.tsx`**:
  - Container component combining header, action trigger, `GenerateKeyModal`, and `VirtualKeysTable`.

### 3. Integration Points

- **`web/src/app/(protected)/clients/page.tsx`**:
  - Server/Client page mounted at `/clients`.
  - Includes breadcrumbs, title, header actions ("Đăng ký thiết bị"), and renders `ClientsTable`.
- **`web/src/features/projects/components/project-workspace-tabs.tsx`**:
  - Replace the placeholder under `<TabsContent value="keys">` with `<VirtualKeysView projectId={project.id} />`.

---

## Implementation Phases & Dependency Graph

```text
Phase 1: Feature 'clients' Setup
├── types/index.ts & client-service.ts
├── use-clients-queries.ts
├── cert-download-dialog.tsx & triggerFileDownload helper
├── register-client-dialog.tsx
├── clients-table.tsx
└── /clients/page.tsx

Phase 2: Feature 'keys' Setup
├── types/index.ts & key-service.ts
├── use-keys-queries.ts
├── generate-key-modal.tsx (two-stage + CLI snippet)
├── virtual-keys-table.tsx (status badge + revoke confirm)
├── virtual-keys-view.tsx
└── project-workspace-tabs.tsx Integration

Phase 3: Verification & Polish
├── Type checking (pnpm --prefix web typecheck)
├── Next.js Production Build (pnpm --prefix web build)
└── End-to-end interactive verification
```

---

## Risk Analysis & Mitigation

| Risk | Impact | Mitigation Strategy |
|---|---|---|
| Private key lost after user accidentally closes modal | High | Display warning modal if user attempts to dismiss before downloading both files, and provide single-click "Tải cả hai tệp". |
| Virtual key generated for revoked device | Medium | In `GenerateKeyModal`, filter out clients where `is_revoked === true` or expiration date is past. |
| Inconsistent query cache after key revocation | Low | Explicitly invalidate `["projects", projectId, "keys"]` on mutation completion. |
| Special characters in client name causing invalid cert CN | Low | Strict Zod validation regex: `/^[a-zA-Z0-9\s._-]+$/`. |
