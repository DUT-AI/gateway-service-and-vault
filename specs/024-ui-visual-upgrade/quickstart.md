# Quickstart Validation Guide: DUT-AI Technical Precision UI Redesign

**Feature**: `024-ui-visual-upgrade`

## Automated Checks
1. `cd web && pnpm typecheck` → 0 TypeScript errors.
2. `cd web && pnpm build` → Production Next.js build succeeds cleanly.
3. `cd web && npx eslint ...` on modified files → 0 errors.

## Visual Inspection Checklist
- `/login` & `/register`: `#042B5F` primary buttons, crisp white card on `#F6F8FC` canvas.
- `/dashboard`: Hero/overview card, metric cards, and quick actions styled with `#042B5F` & `#FFFFFF`.
- `/projects` & `/projects/[id]`: Active tab indicators `#042B5F`, crisp tables (`Vault`, `Virtual Keys`, `Allowed Services`, `Members`, `Settings`).
- `/clients`, `/services`, `/audit`: Consistent `#042B5F` CTAs, active filters, and `JetBrains Mono` identifiers.
