# Research: DUT-AI Technical Precision UI Redesign

**Feature**: `024-ui-visual-upgrade`
**Date**: 2026-11-26

## Design Decisions & Rationale

### 1. Brand Color System (`#042B5F` + `#FFFFFF`)
- **Decision**: Anchor `--primary` to `#042B5F` (`#031F46` hover, `#EEF3FA` tint, `#D6E2F2` subtle border) on `#F6F8FC` workspace canvas and `#FFFFFF` elevated surfaces.
- **Rationale**: Replaces generic `blue-600` (`#2563EB`) and monochrome shadcn defaults with DUT-AI's institutional deep navy identity while maintaining WCAG AA+ contrast (`#FFFFFF` on `#042B5F` has a contrast ratio > 12:1).
- **Semantic Accents**: Keep `#059669` (emerald) for verified/active states, `#D97706` (amber) for quota/one-time warnings, and `#DC2626` (red/rose) for destructive actions (revoke/delete).

### 2. Typography Pairing (`Plus Jakarta Sans` + `JetBrains Mono`)
- **Decision**: Load `Plus_Jakarta_Sans` (`subsets: ["latin", "vietnamese"]`) as `--font-sans` and `JetBrains_Mono` (`subsets: ["latin", "vietnamese"]`) as `--font-mono` in `web/src/app/layout.tsx`, mapped in `globals.css` `@theme inline`.
- **Rationale**: `Plus Jakarta Sans` has crisp geometric proportions and full Vietnamese diacritic support; `JetBrains Mono` ensures tokens, SHA-256 fingerprints, scopes, and CLI commands are effortlessly scannable.

### 3. Technical Precision Light Surface & Chrome Rules
- **Decision**:
  - Use `1px` hairline borders (`#E2E8F0`), subtle elevation (`shadow-2xs` on cards, `shadow-lg` only on modals/popovers), and `0.5rem` (`8px`) / `0.75rem` (`12px`) disciplined radii.
  - Upgrade `AppShell` with a `#042B5F` left-accented active nav pill (`bg-[#042B5F] text-white` or crisp `#EEF3FA` + `#042B5F` left rail), refined top bar, and brand identity (`DUT-AI Gateway & Vault`).
  - Upgrade `Button`, `Card`, `Badge`, `Tabs`, `Input`, `NativeSelect`, `Checkbox`, and `Table` primitives so all pages inherit consistent focus rings (`#042B5F/20`), crisp hover states, and unified padding.
