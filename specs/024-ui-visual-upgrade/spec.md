# Feature Specification: DUT-AI Technical Precision UI Redesign

**Feature Branch**: `024-ui-visual-upgrade`

**Created**: 2026-11-26

**Status**: Clarified & Ready for Planning

**Input**: User description: "Hiện tại tôi thấy dùng shacdn basic thì nhìn UI rất chán => Tôi cần customize UI đẹp lên"

## Design Direction & Clarifications *(from `/speckit-clarify`)*

- **Visual Direction**: **Technical Precision Light** — bright, crisp, high-contrast developer/security console inspired by Linear, Vercel, and Stripe (cool off-white canvas, `#FFFFFF` elevated surfaces, 1px hairline borders, disciplined spacing, zero generic rainbow gradients).
- **Brand & Color Palette**:
  - **Primary Brand Navy**: `#042B5F` (primary CTAs, active navigation indicators, brand anchors, key highlights)
  - **Primary Hover / Deep Navy**: `#031F46`
  - **Surface White**: `#FFFFFF` (cards, tables, dialogs, active tabs)
  - **Canvas Off-White**: `#F6F8FC` (app workspace background)
  - **Subtle Tint**: `#EEF3FA` (active pill backgrounds, subtle navy-tinted callouts)
  - **Hairline Border**: `#E2E8F0` / `#CBD5E1`
  - **Semantic Status**: Emerald `#059669` (active/verified), Amber `#D97706` (warning/quota), Rose/Red `#DC2626` (destructive/revoked)
- **Typography**: `Plus Jakarta Sans` (UI & headings with full Vietnamese support) + `JetBrains Mono` (tokens, fingerprints, key prefixes, CLI snippets, secrets).
- **Scope**: Full platform UI upgrade — Global CSS tokens & typography, `AppShell` / Sidebar / Header, `Dashboard`, `Projects` (and inner tabs: Vault, Virtual Keys, Allowed Services, Members, Settings), `Clients`, `Services`, and `Audit`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Branded Design System Tokens, Typography & AppShell (Priority: P1)

Users open the application and immediately experience a cohesive, custom `#042B5F` & `#FFFFFF` Technical Precision Light identity across typography, surface hierarchy, buttons, badges, inputs, dialogs, and the `AppShell` navigation chrome (replacing `"Project Boilerplate"` metadata and generic shadcn neutral defaults).

**Why this priority**: Updating the root design tokens (`globals.css`), fonts (`layout.tsx`), core UI primitives (`button`, `badge`, `card`, `tabs`, `dialog`, `table`), and `AppShell` establishes the visual foundation inherited by every page.

**Independent Test**: Load `/dashboard` and `/projects` and verify `Plus Jakarta Sans` + `JetBrains Mono` fonts load, `#042B5F` primary tokens and `#F6F8FC` / `#FFFFFF` surfaces render cleanly across sidebar, header, cards, and buttons on both desktop and mobile viewports.

**Acceptance Scenarios**:

1. **Given** any page in the app, **When** rendered, **Then** `<title>` and metadata reflect **DUT-AI Gateway & Vault** (never `"Project Boilerplate"`), and body/monospace text use `Plus Jakarta Sans` and `JetBrains Mono`.
2. **Given** the `AppShell` sidebar and top bar, **When** viewing active nav items and primary actions, **Then** `#042B5F` and `#FFFFFF` provide crisp contrast with subtle hairline dividers (`1px`) and zero generic AI-template clutter.
3. **Given** core shadcn primitives (`Button`, `Card`, `Badge`, `Input`, `Dialog`, `Tabs`), **When** used across features, **Then** default focus rings, primary variants, borders, and radius (`0.5rem`) consistently reflect the `#042B5F` design system.

---

### User Story 2 - Elevated Dashboard & Project Workspace Experience (Priority: P2)

Users navigate `/dashboard`, `/projects`, and `/projects/[id]` (Vault, Virtual Keys, Allowed Services, Members, Settings) and see refined visual hierarchy: clean KPI/summary headers, crisp tabular data density, clear monospace formatting for IDs/prefixes/URLs, and cohesive `#042B5F` active tab states.

**Why this priority**: Dashboard and Project Workspace are where developers and admins spend 90% of their time managing secrets, keys, and services.

**Independent Test**: Inspect `/dashboard`, `/projects`, and all 5 tabs of `/projects/[id]` across `ADMIN`, `PROJECT_DEVELOPER`, and `OTHER` roles and verify visual consistency, table readability, and zero layout regressions.

**Acceptance Scenarios**:

1. **Given** `/dashboard`, **When** loaded, **Then** greeting/hero summary, metric cards, and quick links follow the `#042B5F` + `#FFFFFF` Technical Precision layout with clear typographic hierarchy.
2. **Given** `/projects/[id]`, **When** switching tabs (`Vault`, `Virtual Keys`, `Dịch vụ liên kết`, `Thành viên`, `Cài đặt`), **Then** active tab indicators use `#042B5F`, tables use refined header/row spacing, and monospace identifiers (`key_prefix`, `service_slug`, `scope_name`) render in `JetBrains Mono`.

---

### User Story 3 - Polished Clients, Services, Audit & Onboarding Modals (Priority: P3)

Users interact with `/clients`, `/services`, `/audit`, and key modals (`CertDownloadDialog`, `SdkQuickstartDialog`, `ServiceUsageDialog`, `GenerateKeyModal`) with consistent `#042B5F` primary CTAs, sharp code/CLI blocks, and accessible contrast.

**Why this priority**: Ensures no screen or modal feels left behind with old mismatched generic blue/slate styling.

**Independent Test**: Open `/clients`, `/services`, `/audit`, and trigger `CertDownloadDialog`, `SdkQuickstartDialog`, and `ServiceUsageDialog` to verify cohesive styling and zero TypeScript/ESLint errors.

**Acceptance Scenarios**:

1. **Given** `/clients`, `/services`, `/audit`, and `/login`, **When** viewed, **Then** all primary buttons, active filters, status badges, and table headers align with the `#042B5F` + `#FFFFFF` token system.
2. **Given** onboarding and usage dialogs (`CertDownloadDialog`, `SdkQuickstartDialog`, `ServiceUsageDialog`), **When** opened, **Then** step badges, active tabs, and primary actions use `#042B5F` harmoniously with semantic status feedback.

---

### Edge Cases

- What happens with Vietnamese diacritics in headings and compact badges? `Plus Jakarta Sans` MUST include `vietnamese` subset in `next/font/google` so all Vietnamese glyphs render without fallback font mismatch.
- What happens with destructive actions (Revoke Client, Revoke Key, Delete Secret)? Destructive actions MUST retain clear semantic crimson/rose contrast (`#DC2626`) rather than `#042B5F` so dangerous actions remain unmistakable.
- What happens on mobile viewports (`< 768px`)? Tables remain horizontally scrollable inside crisp `#FFFFFF` containers, and `AppShell` mobile drawer preserves `#042B5F` active states.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `web/src/app/layout.tsx` MUST configure `Plus_Jakarta_Sans` (including `vietnamese` subset) as `--font-sans` and `JetBrains_Mono` as `--font-mono`, and update `<title>` / metadata to **DUT-AI Gateway & Vault**.
- **FR-002**: `web/src/app/globals.css` MUST define semantic CSS custom properties anchored to `#042B5F` (`--primary`), `#FFFFFF` (`--card`, `--primary-foreground`), `#F6F8FC` (`--background`), `#EEF3FA` (`--accent` / `--secondary`), and `#E2E8F0` (`--border`), plus `--font-mono` mapping in `@theme inline`.
- **FR-003**: Core UI primitives in `web/src/components/ui/` (`button.tsx`, `badge.tsx`, `card.tsx`, `tabs.tsx`, `input.tsx`, `table.tsx`, `dialog.tsx`) MUST use semantic design tokens cleanly so primary buttons, active tabs, and focus rings consistently render `#042B5F`.
- **FR-004**: `web/src/components/layout/app-shell.tsx` MUST be upgraded with a crisp `#042B5F` + `#FFFFFF` Technical Precision sidebar and top bar.
- **FR-005**: Feature views across `dashboard`, `projects`, `vault`, `keys`, `clients`, `services`, `audit`, and `auth` MUST replace hardcoded generic `bg-blue-600` / mismatched primary accents with the `#042B5F` design system while preserving all existing RBAC and functional behavior.
- **FR-006**: Frontend build quality gates (`cd web && pnpm typecheck && pnpm build` and `npx eslint` on modified files) MUST pass with zero errors.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of primary interactive elements (primary buttons, active nav items, active tabs, focus rings) use `#042B5F` (`--primary`) on `#FFFFFF` / `#F6F8FC` surfaces.
- **SC-002**: `Plus Jakarta Sans` (with Vietnamese subset) and `JetBrains Mono` render across all UI and code/token elements.
- **SC-003**: `cd web && pnpm typecheck` and `cd web && pnpm build` succeed with 0 errors and zero broken routes.

## Assumptions

- Light-mode **Technical Precision Light** (`#042B5F` + `#FFFFFF` + `#F6F8FC`) is the target theme; no dark-mode toggle is required unless requested later.
- Existing functional logic, API contracts, and RBAC rules remain unchanged.
