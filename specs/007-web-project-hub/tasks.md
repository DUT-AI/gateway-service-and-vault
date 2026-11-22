---
description: "Task list for Web Phase 1 - Project Hub & Core Navigation implementation"
---

# Tasks: Web Phase 1 - Project Hub & Core Navigation

**Input**: Design documents from `/specs/007-web-project-hub/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/projects-api.md`, `quickstart.md`  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.  

## Format: `- [X] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Exact file paths included in all task descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Frontend toast and shared UI layout setup

- [X] T001 Configure Sonner `Toaster` component in `web/src/app/providers.tsx` or `web/src/app/layout.tsx` for global user feedback
- [X] T002 [P] Verify and ensure all needed `shadcn/ui` components (`dialog`, `table`, `tabs`, `badge`, `dropdown-menu`, `select`, `skeleton`, `sonner`, `card`, `button`, `input`, `label`) are exported in `web/src/components/ui/index.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data layer, HTTP service client, and React Query hooks required by all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Define `Project` types and DTO mappings using `Schema<"ProjectResponse">` in `web/src/features/projects/types/index.ts`
- [X] T004 [P] Implement `ProjectService` Axios HTTP client functions (`listProjects`, `getProjectById`, `createProject`) in `web/src/features/projects/services/project-service.ts`
- [X] T005 Implement TanStack React Query hooks (`useProjectsQuery`, `useProjectDetailQuery`, `useCreateProjectMutation`) with query key management and cache invalidation in `web/src/features/projects/hooks/use-projects-queries.ts`
- [X] T006 Export project types, services, and query hooks in `web/src/features/projects/index.ts`

**Checkpoint**: Data foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - AppShell Navigation & Project Directory Listing (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can view their live SSO profile in the persistent AppShell, navigate between workspaces, and view the project directory card grid with responsive layout, empty states, and skeleton loaders.

**Independent Test**: Log in via SSO, navigate to `/projects`, see user profile badge in AppShell, view project cards fetched from `GET /api/v1/gateway/projects`, or observe inviting empty state when 0 projects exist.

### Implementation for User Story 1

- [X] T007 [US1] Update `AppShell` navigation in `web/src/components/layout/app-shell.tsx` with active route detection for Dashboard (`/dashboard`), Projects (`/projects`), Clients (`/clients`), and Services (`/services`), rendering live user avatar and authenticated badge
- [X] T008 [P] [US1] Implement `ProjectCard` component in `web/src/features/projects/components/project-card.tsx` rendering project title, slug badge, description, and formatted creation date
- [X] T009 [P] [US1] Implement `ProjectList` component in `web/src/features/projects/components/project-list.tsx` supporting responsive grid display, skeleton card shimmer loaders, and inviting empty state illustration
- [X] T010 [US1] Create Project Directory page in `web/src/app/(protected)/projects/page.tsx` integrating `ProjectList` and action header
- [X] T011 [US1] Update Dashboard overview in `web/src/app/(protected)/dashboard/page.tsx` to display project summary cards and direct navigation links to `/projects`

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently (MVP ready!)

---

## Phase 4: User Story 2 - Interactive Project Creation & Slug Generation (Priority: P2)

**Goal**: Users can create a new project via a modal dialog with real-time kebab-case slug suggestion from project name and client-side Zod validation.

**Independent Test**: Click "Tạo dự án mới", type a project name (e.g. "Payment Gateway Core"), observe auto-generated slug `payment-gateway-core`, submit form -> dialog closes, success toast appears, and project appears on the list.

### Implementation for User Story 2

- [X] T012 [P] [US2] Define Zod validation schema `createProjectSchema` and Vietnamese-aware auto-slug helper function in `web/src/features/projects/types/form-schemas.ts`
- [X] T013 [US2] Implement `CreateProjectDialog` component in `web/src/features/projects/components/create-project-dialog.tsx` using `Dialog`, `react-hook-form`, `useCreateProjectMutation`, auto-slug suggestion, pending button state, and Sonner toast
- [X] T014 [US2] Wire `CreateProjectDialog` into `web/src/app/(protected)/projects/page.tsx` header button and `ProjectList` empty state CTA button

**Checkpoint**: At this point, User Stories 1 AND 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Project Overview & Workspace Header with Breadcrumbs (Priority: P3)

**Goal**: Clicking any project card opens the dedicated project workspace (`/projects/[id]`) with breadcrumbs, project metadata, and sub-tabs for Dynamic Vault, Virtual Keys, and Settings.

**Independent Test**: Click a project card, navigate to `/projects/[id]`, observe `Dự án > [Tên dự án]` breadcrumbs, view project header info, switch between workspace sub-tabs, and handle 404 for invalid project IDs.

### Implementation for User Story 3

- [X] T015 [P] [US3] Implement `Breadcrumbs` component in `web/src/components/layout/breadcrumbs.tsx` with accessible navigation links
- [X] T016 [P] [US3] Implement `ProjectHeader` component in `web/src/features/projects/components/project-header.tsx` displaying project name, slug badge, description, and created timestamp
- [X] T017 [P] [US3] Implement `ProjectWorkspaceTabs` component in `web/src/features/projects/components/project-workspace-tabs.tsx` rendering `Tabs` for "Biến môi trường (Vault)", "Virtual Keys", and "Cài đặt" with empty placeholders ready for future phases
- [X] T018 [US3] Create Project Workspace Detail page in `web/src/app/(protected)/projects/[id]/page.tsx` integrating `ProjectHeader`, `ProjectWorkspaceTabs`, `Breadcrumbs`, loading skeletons, and 404 Project Not Found state

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Packaging, typecheck validation, build verification, and clean exports

- [X] T019 [P] Export all project components in `web/src/features/projects/components/index.ts`
- [X] T020 Run quickstart validation from `specs/007-web-project-hub/quickstart.md` (`pnpm --prefix web typecheck && pnpm --prefix web build`)
- [X] T021 Validate responsive mobile slide-over drawer and mobile viewports (<768px) across all created views

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start immediately after Foundational (MVP!)
  - User Story 2 (P2): Depends on Foundational mutation hook & US1 list page
  - User Story 3 (P3): Depends on Foundational detail hook & US1 project card links
- **Polish (Phase 6)**: Depends on all user stories being complete
