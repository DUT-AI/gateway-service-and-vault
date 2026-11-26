---

description: "Task list for DUT-AI Technical Precision UI Redesign"
---

# Tasks: DUT-AI Technical Precision UI Redesign

**Input**: Design documents from `specs/024-ui-visual-upgrade/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `contracts/design-tokens.md`, `quickstart.md`

**Organization**: Tasks are grouped by visual layer and user story for incremental, non-breaking rollout.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Design System Tokens, Typography & Core UI Primitives (US1 🎯 MVP)

- [x] T001 [P] [US1] Configure `Plus_Jakarta_Sans` (`vietnamese`, `latin`) + `JetBrains_Mono`, `NextTopLoader` (`#042B5F`), and **DUT-AI Gateway & Vault** metadata in `web/src/app/layout.tsx`
- [x] T002 [P] [US1] Define Technical Precision Light tokens (`#042B5F` primary, `#FFFFFF` surface, `#F6F8FC` canvas, `#EEF3FA` accent, `#E2E8F0` border, `--font-mono`) in `web/src/app/globals.css`
- [x] T003 [P] [US1] Upgrade core UI primitives (`button.tsx`, `card.tsx`, `badge.tsx`, `tabs.tsx`, `input.tsx`, `native-select.tsx`, `checkbox.tsx`, `table.tsx`) in `web/src/components/ui/` to inherit `#042B5F` primary/focus styling and refined borders/spacing
- [x] T004 [US1] Redesign `web/src/components/layout/app-shell.tsx` and `web/src/components/layout/breadcrumbs.tsx` with crisp `#042B5F` + `#FFFFFF` sidebar, active indicators, and refined top bar

---

## Phase 2: Dashboard, Auth & Project Workspace (US2)

- [x] T005 [P] [US2] Upgrade `web/src/app/(protected)/dashboard/page.tsx` and `web/src/features/auth/components/{login-form.tsx,register-form.tsx}` with `#042B5F` brand anchors and Technical Precision card hierarchy
- [x] T006 [P] [US2] Upgrade Projects overview & workspace (`web/src/app/(protected)/projects/**`, `web/src/features/projects/components/{project-card.tsx,project-header.tsx,project-list.tsx,project-workspace-tabs.tsx,create-project-dialog.tsx,project-members-view.tsx,project-allowed-services-view.tsx,allowed-services-table.tsx,bind-service-dialog.tsx,edit-service-quota-dialog.tsx,service-usage-dialog.tsx}`) to `#042B5F` + `#FFFFFF` tokens
- [x] T007 [P] [US2] Upgrade Vault & Virtual Keys views (`web/src/features/vault/components/*` and `web/src/features/keys/components/*`) to `#042B5F` primary accents and `JetBrains Mono` formatting

---

## Phase 3: Clients, Services, Audit & Onboarding Modals (US3)

- [x] T008 [P] [US3] Upgrade Clients pages & onboarding modals (`web/src/app/(protected)/clients/page.tsx`, `web/src/features/clients/components/*`) to `#042B5F` primary CTAs, active scope/type tabs, and step badges
- [x] T009 [P] [US3] Upgrade Services & Audit views (`web/src/app/(protected)/services/page.tsx`, `web/src/features/services/components/*`, `web/src/features/audit/components/audit-logs-table.tsx`) to `#042B5F` + `#FFFFFF` Technical Precision styling

---

## Phase 4: Verification & Quality Gates

- [x] T010 Run `cd web && pnpm typecheck && pnpm build` and verify zero TypeScript, ESLint, or Next.js build errors
