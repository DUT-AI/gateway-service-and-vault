# Implementation Plan: Web Phase 1 - Project Hub & Core Navigation

**Branch**: `007-web-project-hub` | **Date**: 2026-11-23 | **Spec**: [specs/007-web-project-hub/spec.md](spec.md)

**Input**: Feature specification from `specs/007-web-project-hub/spec.md` (Giai đoạn 1: Cấu trúc khung AppShell, SSO user identity, danh sách dự án, tạo dự án mới, chi tiết dự án & tabs).

## Summary

Build the foundational Project Hub and Navigation for the Secure API Gateway & Dynamic Vault web platform. This includes upgrading the persistent `AppShell` with full sidebar navigation and live DUT-AI SSO profile context, building the responsive Project Directory (`/projects`) with card grid, search, and empty state, implementing the accessible Project Creation dialog with real-time slug generation, and establishing the Project Detail workspace (`/projects/[id]`) with breadcrumbs and workspace sub-tabs ready for Dynamic Vault (Phase 2) and Virtual Keys (Phase 3).

## Technical Context

**Language/Version**: TypeScript 5.9, React 19, Next.js 16.2.4 (App Router with Turbopack)  
**Primary Dependencies**: `@tanstack/react-query` v5, `axios`, `react-hook-form`, `zod`, `@hookform/resolvers`, `lucide-react`, `class-variance-authority`, `sonner`, `radix-ui` primitives  
**Storage**: Client-side state managed via TanStack Query cache; backend persistence via FastAPI PostgreSQL models  
**Testing**: `pnpm --prefix web typecheck` (tsc `--noEmit`), `pnpm --prefix web build` (Next.js production build verification), and Pytest integration verification (`test_gateway_management_api.py`)  
**Target Platform**: Modern desktop & mobile web browsers (Chrome, Safari, Firefox, Edge)  
**Project Type**: Next.js App Router Web Application  
**Performance Goals**: First Contentful Paint < 1.0s, page transition latency < 150ms, 60fps animations for dialogs and drawer transitions  
**Constraints**: Zero custom non-type-safe interfaces; 100% type generation from `api.generated.d.ts`; zero hydration mismatch warnings  
**Scale/Scope**: Supporting hundreds of projects and organizations with responsive card grids and client-side filtering  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Clean Architecture & Domain Purity**: PASS. The frontend interacts strictly through public REST API contracts (`/api/v1/gateway/projects`, `/api/v1/auth/me`). Pure client application without inline server database access or leaked backend domain internals.
- **Principle IV: Offline Contract & Type Synchronization**: PASS. All API payloads and response schemas strictly use `Schema<"ProjectResponse">` and `Schema<"ProjectCreateRequest">` generated from OpenAPI via `make api-types`.
- **Principle V: Standardized DUT-AI SSO & Strict Integer User ID**: PASS. Current user profile in AppShell directly displays SSO identity with native integer ID (`id: int`).
- **Technology Standards**: PASS. Built with Next.js 16 App Router, React 19, Tailwind CSS v4, and Radix UI / shadcn design tokens.

## Project Structure

### Documentation (this feature)

```text
specs/007-web-project-hub/
├── plan.md              # This implementation plan
├── research.md          # Technical decisions (App Router, TanStack Query, shadcn, auto-slug)
├── data-model.md        # Frontend entities, form schemas, and tab keys
├── quickstart.md        # End-to-end browser & automated validation guide
└── contracts/
    └── projects-api.md  # Contract definitions for project list, get, create, and SSO profile
```

### Source Code Layout (repository root)

```text
web/src/
├── app/
│   └── (protected)/
│       ├── layout.tsx                   # AppShell wrapping all authenticated views
│       ├── dashboard/page.tsx           # High-level dashboard overview
│       └── projects/
│           ├── page.tsx                 # Projects directory page (US1, US2)
│           └── [id]/page.tsx            # Project detail workspace & tabs (US3)
├── components/
│   ├── layout/
│   │   ├── app-shell.tsx                # Persistent sidebar, mobile drawer, header, SSO profile
│   │   └── breadcrumbs.tsx              # Reusable breadcrumb navigation component
│   └── ui/                              # shadcn/ui primitives (Dialog, Button, Input, Card, Badge, Tabs, Skeleton, Sonner)
├── features/
│   └── projects/
│       ├── types/index.ts               # Project types re-exported from api.generated.d.ts
│       ├── hooks/
│       │   ├── use-projects-queries.ts  # useProjectsQuery, useProjectDetailQuery, useCreateProjectMutation
│       │   └── index.ts
│       ├── components/
│       │   ├── project-list.tsx         # Card grid, empty state, skeleton loading
│       │   ├── project-card.tsx         # Individual project summary card with slug badge & date
│       │   ├── create-project-dialog.tsx# Modal dialog with auto-slug generator & Zod validation
│       │   ├── project-header.tsx       # Workspace header with metadata & slug tag
│       │   ├── project-workspace-tabs.tsx # Tabs (Dynamic Vault, Virtual Keys, Settings)
│       │   └── index.ts
│       ├── services/
│       │   ├── project-service.ts       # Axios client functions for projects API
│       │   └── index.ts
│       └── index.ts
```

**Structure Decision**: Clean feature-based organization under `web/src/features/projects/` keeping components, hooks, services, and schemas grouped together, completely decoupled from page route wrappers in `web/src/app/`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | Architecture strictly complies with all project principles | N/A |
