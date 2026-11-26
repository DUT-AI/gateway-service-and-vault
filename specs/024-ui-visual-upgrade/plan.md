# Implementation Plan: DUT-AI Technical Precision UI Redesign

**Branch**: `024-ui-visual-upgrade` | **Date**: 2026-11-26 | **Spec**: [spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/024-ui-visual-upgrade/spec.md)

**Input**: Feature specification from `/specs/024-ui-visual-upgrade/spec.md`

## Summary

Upgrade the entire Next.js frontend from generic shadcn defaults to a custom **Technical Precision Light** design system anchored on **`#042B5F`** (Deep Navy) and **`#FFFFFF`**, powered by `Plus Jakarta Sans` + `JetBrains Mono` typography, refined `AppShell` chrome, cohesive UI primitives, and consistent feature views across Dashboard, Projects, Vault, Virtual Keys, Clients, Services, Audit, and Auth.

## Technical Context

**Language/Version**: TypeScript 5 / React 19 / Next.js 16 (App Router)  
**Primary Dependencies**: Tailwind CSS v4, Radix UI / shadcn primitives, `lucide-react`, `next/font/google`  
**Storage**: N/A (pure frontend UI/UX redesign)  
**Testing**: `cd web && pnpm typecheck`, `cd web && pnpm build`, `npx eslint`  
**Target Platform**: Desktop & mobile web browsers  
**Project Type**: Next.js web application (`web/src/`)  
**Performance Goals**: Zero layout shift on font load (`next/font/google`), zero runtime regressions  
**Constraints**: Preserve all existing RBAC guards, form validations, and API hooks; zero backend changes  
**Scale/Scope**: Global tokens, layout, ~8 UI primitives, and feature views across 7 modules

## Constitution Check

- **IV. Offline Contract & Type Synchronization**: Pass — no API types altered.
- **V. Standardized 3-Tier RBAC**: Pass — all `isAdmin`, `isDeveloper`, `isOtherRole` UI guards preserved.

## Project Structure

```text
web/src/
├── app/
│   ├── globals.css                     # #042B5F + #FFFFFF + #F6F8FC tokens & @theme inline
│   ├── layout.tsx                      # Plus Jakarta Sans + JetBrains Mono + DUT-AI metadata
│   ├── page.tsx                        # Branded landing/redirect polish
│   └── (protected)/                    # Dashboard, Projects, Clients, Services, Audit pages
├── components/
│   ├── layout/                         # AppShell & Breadcrumbs Technical Precision upgrade
│   └── ui/                             # Button, Card, Badge, Tabs, Input, NativeSelect, Checkbox, Table
└── features/
    ├── auth/                           # Login & Register polish
    ├── projects/                       # Project cards, header, workspace tabs, allowed services, members
    ├── vault/                          # Vault view, scope tabs, secrets table, dialogs
    ├── keys/                           # Virtual keys view, table, generate modal
    ├── clients/                        # Clients toolbar, table, onboarding dialogs
    ├── services/                       # Services table & create dialog
    └── audit/                          # Audit logs table
```

## Complexity Tracking

No constitution violations; no complexity exceptions required.
