---

description: "Task list for Self-Service mTLS Client & Key UX + Ownership Scoping"
---

# Tasks: Self-Service mTLS Client & Key UX + Ownership Scoping

**Input**: Design documents from `specs/020-mtls-client-ux-scoping/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/clients-ux-api.md`

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story, strictly adhering to Constitution v2.3.0.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Foundational Exceptions & DTO Contracts

**Purpose**: Prepare domain exception and self-issued DTO schema before updating use cases and routers.

- [x] T001 [P] Add `ClientOwnershipDeniedError` to `modules/gateway/use_cases/exceptions.py` and export in `modules/gateway/use_cases/__init__.py`
- [x] T002 [P] Make `RegisterClientRequest.owner_id` optional (`str | None = None`) in `modules/gateway/dtos/gateway_dtos.py`

---

## Phase 2: User Story 1 & 2 - Backend Ownership Scoping & Admin Governance (Priority: P1/P2) 🎯 MVP

**Goal**: Enforce self-issued `owner_id` on `POST /clients`, scope `GET /clients` to own devices for Developers (all devices for Admins), and enforce ownership on `POST /clients/{id}/revoke`.

**Independent Test**: Developer A cannot see or revoke Developer B's clients (`403 Forbidden`) and cannot spoof `owner_id`; Admin sees and can revoke any client.

- [x] T003 [US1] Update `ListRegisteredClientsUseCase.execute(owner_id: str | None = None, is_admin: bool = False)` in `modules/gateway/use_cases/list_registered_clients.py`
- [x] T004 [US1] Update `RevokeClientUseCase.execute(client_id: str, caller_owner_id: str | None = None, is_admin: bool = False)` in `modules/gateway/use_cases/revoke_client.py` to raise `ClientOwnershipDeniedError` on mismatch
- [x] T005 [US1] [US2] Update `apps/api/routers/gateway/clients.py` to pass `user_ctx.user_id` & `user_ctx.is_admin` to `list_clients` and `revoke_client` (mapping `ClientOwnershipDeniedError` -> `HTTP 403`), and lock `owner_id = str(user_ctx.user_id)` in `register_client`

**Checkpoint**: Backend ownership isolation and self-issued mTLS registration enforced.

---

## Phase 3: User Story 3 - Frontend Self-Service UX, SSO Owner Profiles & Onboarding Guidance (Priority: P3)

**Goal**: Display human-readable SSO owner profiles (avatar, name, email) in `ClientsTable`, add Admin scope tabs ("Tất cả hệ thống" vs "Thiết bị của tôi"), and guide users to Project detail -> Virtual Keys after cert download.

**Independent Test**: Clients table renders SSO avatar/name/email; Admin sees "Tất cả hệ thống" / "Thiết bị của tôi" tabs; CertDownloadDialog links to `/projects`.

- [x] T006 [P] [US3] Update `web/src/features/clients/components/clients-table.tsx` to resolve `owner_id` via `useUserOptionsQuery` (avatar, name, email) and add Admin scope filter tabs ("Tất cả hệ thống" vs "Thiết bị của tôi")
- [x] T007 [P] [US3] Update `web/src/features/clients/components/cert-download-dialog.tsx` to include a next-step callout and link to `/projects` explaining how to generate Virtual Keys inside the Project's Virtual Keys tab
- [x] T008 [P] [US3] Update `web/src/features/clients/components/register-client-dialog.tsx` to clarify self-issued ownership in UI copy

---

## Phase 4: Verification, Type Sync & Quality Gates

**Purpose**: Sync OpenAPI types, write integration tests for client ownership scoping, and run full verification.

- [x] T009 [P] Run `make api-types` to sync updated `RegisterClientRequest` into `web/src/types/api.generated.d.ts`
- [x] T010 Write integration test suite `tests/integration/test_client_ownership_scoping.py` covering `ADMIN` vs `PROJECT_DEVELOPER` visibility, `owner_id` anti-spoofing, and `403` on cross-user revoke
- [x] T011 Run `uv run ruff check --fix && uv run ruff format`, `cd web && pnpm typecheck`, and `uv run pytest`
