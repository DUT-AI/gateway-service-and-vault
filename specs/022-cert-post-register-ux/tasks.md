---

description: "Task list for Post-Registration Certificate Onboarding UX"
---

# Tasks: Post-Registration Certificate Onboarding UX

**Input**: Design documents from `specs/022-cert-post-register-ux/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/cert-onboarding-ui.md`, `quickstart.md`

**Organization**: Tasks are grouped by user story, keeping all UI changes modular under `web/src/features/clients/`.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Foundational Filename Helper

- [x] T001 [P] Add `getClientCertFilenames(deviceName: string)` returning `{ crtFilename, keyFilename }` in `web/src/features/clients/utils/download-file.ts`

---

## Phase 2: User Story 1 - Guided Step-by-Step Post-Registration Flow (Priority: P1) 🎯 MVP

- [x] T002 [P] [US1] Create `CertInstallInstructions` component in `web/src/features/clients/components/cert-install-instructions.tsx` with `macOS / Linux`, `Windows`, and `Docker` tabs and 1-click copyable setup commands using exact sanitized filenames
- [x] T003 [P] [US1] Create `CertNextStepsCard` component in `web/src/features/clients/components/cert-next-steps-card.tsx` adapting guidance to `useAuth().isOtherRole` (handoff message copy for Regular Dev vs `/projects` CTA & Docker guide trigger for Project Developer/Admin)
- [x] T004 [US1] Refactor `CertDownloadDialog` in `web/src/features/clients/components/cert-download-dialog.tsx` into a 3-step guided onboarding flow integrating `getClientCertFilenames`, `CertInstallInstructions`, and `CertNextStepsCard`

---

## Phase 3: User Story 2 - Safe Dismissal & Zero-Loss Guardrails (Priority: P2)

- [x] T005 [US2] Intercept all dialog close triggers (`onOpenChange(false)`, `X`, backdrop, Escape, and footer button) in `web/src/features/clients/components/cert-download-dialog.tsx` when `!downloadedKey`
- [x] T006 [P] [US2] Pass `key={downloadBundle?.id ?? "closed"}` to `CertDownloadDialog` in `web/src/features/clients/components/clients-table.tsx` so download tracking resets cleanly per registered device

---

## Phase 4: User Story 3 - Quick SDK Verification Snippet (Priority: P3)

- [x] T007 [US3] Add a compact copyable quick-check verification snippet (`dut-vault run` / `curl --cert ~/.dut-vault/client.crt --key ~/.dut-vault/client.key`) inside `web/src/features/clients/components/cert-next-steps-card.tsx`

---

## Phase 5: Verification & Quality Gates

- [x] T008 Run `cd web && pnpm typecheck` and `npx eslint` on all modified/created files in `web/src/features/clients/` to verify 0 TypeScript and ESLint errors
