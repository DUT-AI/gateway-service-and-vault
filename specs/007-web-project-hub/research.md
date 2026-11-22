# Research & Technical Decisions: Web Phase 1 - Project Hub & Core Navigation

**Feature**: `007-web-project-hub`  
**Date**: 2026-11-23  

## 1. Technical Decisions

### Decision 1: Next.js 16 App Router Structure for Projects Workspace
- **Decision**: Organize routes under `web/src/app/(protected)/projects/` with:
  - `web/src/app/(protected)/projects/page.tsx`: Project directory (grid listing, search, empty state).
  - `web/src/app/(protected)/projects/[id]/page.tsx`: Dynamic project workspace (header, metadata, sub-tabs).
- **Rationale**:
  - Encapsulated within `(protected)` route group ensuring auth guard and persistent `AppShell` layout are shared without re-rendering the sidebar on navigation.
  - Next.js dynamic routing with `params: Promise<{ id: string }>` conforming to React 19 / Next.js 16 App Router asynchronous conventions.
- **Alternatives Considered**:
  - Flat route `/projects` without `(protected)` group: Rejected because it duplicates layout hierarchy and auth verification logic.

---

### Decision 2: TanStack React Query v5 Data Fetching & Cache Invalidation
- **Decision**: Encapsulate all API interactions inside `web/src/features/projects/hooks/use-projects-queries.ts`:
  - `useProjectsQuery()`: Queries `GET /api/v1/gateway/projects` using `queryKey: ["projects"]`.
  - `useProjectDetailQuery(projectId)`: Queries `GET /api/v1/gateway/projects/{projectId}` using `queryKey: ["projects", projectId]`.
  - `useCreateProjectMutation()`: Calls `POST /api/v1/gateway/projects`, and on success invalidates `["projects"]` query cache and triggers Sonner toast notification.
- **Rationale**:
  - Automatic background refetching, query deduplication, loading states, and clean optimistic cache invalidation.
  - Decouples UI components from HTTP transport specifics.
- **Alternatives Considered**:
  - Direct Axios calls inside `useEffect`: Rejected due to race conditions, manual loading state boilerplate, and lack of automatic cache invalidation.

---

### Decision 3: Form State Management & Validation with React Hook Form + Zod
- **Decision**: Use `react-hook-form` paired with `@hookform/resolvers/zod` in `CreateProjectDialog`:
  - Validation schema:
    ```typescript
    export const createProjectSchema = z.object({
      name: z.string().min(2, "Tên dự án tối thiểu 2 ký tự").max(100, "Tên dự án tối đa 100 ký tự"),
      slug: z.string().min(2, "Mã slug tối thiểu 2 ký tự").max(100, "Mã slug tối đa 100 ký tự").regex(/^[a-z0-9-]+$/, "Slug chỉ được chứa chữ thường, số và dấu gạch ngang (-)"),
      description: z.string().max(500, "Mô tả tối đa 500 ký tự").optional(),
    });
    ```
  - Auto-slug generator: As the user types the project name, convert Vietnamese characters and spaces to lower-kebab-case in real time, while retaining custom manual edits if the user explicitly modifies the slug.
- **Rationale**:
  - High-performance uncontrolled form inputs with minimal re-renders.
  - Real-time client-side feedback prevents invalid backend submissions.
- **Alternatives Considered**:
  - Manual `useState` for each field: Rejected due to repetitive validation handling and boilerplate.

---

### Decision 4: UI Component Architecture with `shadcn/ui` Primitives
- **Decision**: Leverage pre-installed `shadcn/ui` components from `web/src/components/ui/`:
  - `Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogFooter` for project creation modal.
  - `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent` for project directory grid.
  - `Button` with `asChild` support for seamless Next.js `<Link>` wrapping.
  - `Badge` for project slug and status tags.
  - `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent` for the workspace sub-navigation.
  - `Skeleton` for shimmer loading placeholders.
  - `sonner` (`toast.success`, `toast.error`) for feedback notifications.
- **Rationale**:
  - Consistent design language, full accessibility (ARIA, focus management), zero custom CSS churn.
- **Alternatives Considered**:
  - Writing raw Tailwind HTML cards and modal backdrops from scratch: Rejected because shadcn primitives handle accessibility, ESC key, and focus traps out-of-the-box.

---

### Decision 5: AppShell Navigation & Active Route Highlighting
- **Decision**: Update `web/src/components/layout/app-shell.tsx`:
  - Expand `NAV_ITEMS`:
    - Dashboard (`/dashboard`)
    - Dự án / Projects (`/projects`)
    - Thiết bị mTLS / Clients (`/clients`)
    - Dịch vụ / Services (`/services`)
  - Highlight active item when pathname starts with `/projects`.
  - Add Breadcrumb navigation at the top bar when inside `/projects/[id]`.
- **Rationale**:
  - Unifies multi-page navigation across all phases of the platform.
