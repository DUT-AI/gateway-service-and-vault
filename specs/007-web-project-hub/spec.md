# Feature Specification: Web Phase 1 - Project Hub & Core Navigation

**Feature Branch**: `007-web-project-hub`

**Created**: 2026-11-23

**Status**: Draft

**Input**: User description: "Hãy code giai đoạn 1 cho tôi" based on Phase 1 in `docs/WEB_ROADMAP.md` ("Giai Đoạn 1: Cấu Trúc Khung & Quản Lý Dự Án (Project Hub) - Hoàn thiện App Shell (Sidebar, Header, Breadcrumbs), tích hợp SSO profile và màn hình quản lý danh sách/chi tiết dự án").

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Modern AppShell Navigation & Project Directory Listing (Priority: P1) 🎯 MVP

As an authenticated developer or administrator logged in via DUT-AI SSO, I want an intuitive, persistent navigation layout (AppShell) that displays my SSO profile and provides an interactive directory of all business projects, so that I can see the workspaces I have access to and select one to manage.

**Why this priority**: Core entry point of the entire web application. Without the project hub and global navigation, users cannot navigate to project-specific vaults, keys, or gateway configurations.

**Independent Test**: An authenticated user accesses `/projects` (or `/dashboard`), views their live SSO user profile (avatar, name, email, roles) in the AppShell, and sees a responsive card grid showing all registered projects with their title, slug badge, description, and creation date.

**Acceptance Scenarios**:

1. **Given** an authenticated user navigating to `/projects`, **When** the page loads, **Then** the system queries `GET /api/v1/gateway/projects` and renders a card grid of all projects with name, slug, description, and formatted creation date.
2. **Given** an authenticated user, **When** viewing the persistent AppShell, **Then** the user's name, email, avatar, and authenticated DUT badge are displayed, with a working Logout action that clears the session.
3. **Given** a platform state where zero projects exist, **When** the user loads `/projects`, **Then** the page renders an informative Empty State with an icon, explanatory message, and a primary action button to "Create First Project".
4. **Given** a slow network connection, **When** project data is being fetched, **Then** accessible Skeleton card loaders are displayed in place of the project cards.

---

### User Story 2 - Interactive Project Creation & Slug Generation (Priority: P2)

As a team lead or administrator, I want to create a new project directly from the web interface using an accessible modal dialog with immediate validation, so that our team can immediately establish an isolated security boundary for secrets and gateway routing.

**Why this priority**: Enables self-service onboarding of new applications and services without requiring direct database access or manual API calls.

**Independent Test**: Click the "Tạo dự án mới" button, enter a project name, observe automatic slug generation (or enter custom slug) and description, submit the form, and verify the new project immediately appears in the projects list with a confirmation toast notification.

**Acceptance Scenarios**:

1. **Given** a user viewing the projects page, **When** they click "Tạo dự án mới" (Create Project), **Then** a modal dialog (`Dialog`) opens displaying fields for Project Name (required), Slug (required), and Description (optional).
2. **Given** the user entering a project name (e.g. "Payment Service"), **When** typing in the name field, **Then** the slug field automatically suggests an URL-safe slug (e.g. "payment-service") if not manually overridden.
3. **Given** invalid input (such as an empty name or a slug containing special characters), **When** the user submits the form, **Then** localized validation messages are displayed under the relevant inputs and no network request is sent.
4. **Given** valid input, **When** the user clicks "Tạo dự án", **Then** the dialog shows a pending loading spinner on the submit button, sends `POST /api/v1/gateway/projects`, closes the dialog upon 201 response, triggers a success toast, and refreshes the project list cache.

---

### User Story 3 - Project Overview & Workspace Header with Breadcrumb Navigation (Priority: P3)

As a developer or administrator, I want to click on any project card to enter that specific project's workspace (`/projects/[id]`), view project metadata, navigate through a tabbed workspace header, and use breadcrumbs to jump back, so that I have a dedicated control plane for that project's secrets, virtual keys, and gateway settings.

**Why this priority**: Establishes the layout anchor and sub-navigation structure required for Phase 2 (Dynamic Vault secrets table) and Phase 3 (Virtual keys).

**Independent Test**: Click on a project card from `/projects`, verify routing to `/projects/[id]`, observe breadcrumb `Dự án > [Tên dự án]`, inspect project metadata header, and verify switching between tabs ("Biến môi trường / Vault", "Virtual Keys", "Cài đặt") updates the URL/view smoothly.

**Acceptance Scenarios**:

1. **Given** a user clicking on a project card, **When** navigation completes, **Then** the browser routes to `/projects/[id]` and queries `GET /api/v1/gateway/projects/{id}`.
2. **Given** a valid project ID, **When** the project detail page renders, **Then** the page displays a header containing the project name, slug badge, description, creation date, and breadcrumb navigation link back to `/projects`.
3. **Given** the project workspace view, **When** viewing the sub-navigation tabs, **Then** tabs for "Biến môi trường (Vault)", "Virtual Keys", and "Cài đặt" are present and accessible.
4. **Given** a user navigating to a non-existent project ID (e.g. `/projects/invalid-id`), **When** the backend returns 404, **Then** the page displays a friendly "Project Not Found" error state with an action button to return to the projects list.

---

### Edge Cases

- **Session Expiry During Navigation**: If the user's SSO access token expires while browsing or creating a project, Axios 401 interceptor MUST clear auth state and redirect to `/login` without crashing.
- **Duplicate Project Slug**: If a user submits a slug that already exists in the system, backend returns 400/409, and the dialog MUST display a clear error message ("Mã định danh slug này đã tồn tại") without losing the user's form inputs.
- **Mobile Responsive Drawer**: On viewport widths under 768px, the sidebar MUST collapse into a mobile drawer with smooth slide-over animation and backdrop tap-to-dismiss.
- **Rapid Navigation / Invalidation**: Switching quickly between projects MUST cancel stale queries via TanStack Query without displaying mismatched project details.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Domain 1: Application Shell & SSO Context
- **FR-001**: System MUST provide a responsive desktop sidebar and mobile slide-over drawer navigation containing links to Dashboard, Projects, Clients, and Services.
- **FR-002**: System MUST render authenticated user profile details (`name`, `email`, `role`, `avatar`) fetched from `GET /api/v1/auth/me`.
- **FR-003**: System MUST provide a global Logout button that clears local tokens and invokes `POST /api/v1/auth/logout`.
- **FR-004**: System MUST maintain the DUT-AI Waffle launcher menu in the top bar for cross-application navigation.

#### Domain 2: Project Hub Listing & Display
- **FR-005**: System MUST query `GET /api/v1/gateway/projects` and render projects as responsive cards displaying project title, slug, description, and human-readable creation timestamp.
- **FR-006**: System MUST show an empty state illustration with an action button to create the first project when the project list is empty.
- **FR-007**: System MUST show accessible skeleton placeholder cards while project data is in a loading state.

#### Domain 3: Project Creation & Validation
- **FR-008**: System MUST provide a modal dialog (`Dialog`) for creating projects with inputs for name (min 2, max 100 chars), slug (min 2, max 100 chars, regex `^[a-z0-9-]+$`), and optional description.
- **FR-009**: System MUST automatically generate an URL-safe slug proposal from the project name input in real time, while allowing custom manual edits.
- **FR-010**: System MUST validate form inputs using Zod and display localized inline error messages.
- **FR-011**: On successful project creation (`POST /api/v1/gateway/projects`), system MUST invalidate the projects query cache, close the dialog, and display a success toast via `Sonner`.

#### Domain 4: Project Workspace Detail & Tabs
- **FR-012**: System MUST support dynamic routing to `/projects/[id]` and fetch project details via `GET /api/v1/gateway/projects/{id}`.
- **FR-013**: System MUST provide breadcrumb navigation displaying `Dự án > [Tên dự án]`.
- **FR-014**: System MUST render workspace tabs (`Tabs`) for "Dynamic Vault", "Virtual Keys", and "Cài đặt" as architectural anchors for subsequent development phases.
- **FR-015**: System MUST handle 404 Project Not Found errors gracefully with an informative empty state and return button.

---

### Key Entities

- **Project**: Represents a security and business workspace boundary. Attributes include `id: str` (ULID), `name: str`, `slug: str`, `description: str | None`, and `created_at: datetime`.
- **UserSession**: Current authenticated session extracted from SSO. Attributes include integer user `id: int`, `email: str`, `name: str | None`, `role: str`, `roles: list[str]`, and `permissions: list[str]`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view the full project directory within 1.5 seconds of page load on standard 4G/broadband connections.
- **SC-002**: Users can complete creating a new project in under 30 seconds from clicking the create button to seeing it on the dashboard.
- **SC-003**: 100% of form validation errors occur client-side without unnecessary network roundtrips.
- **SC-004**: Zero TypeScript compilation errors (`tsc --noEmit`) and zero ESLint errors across all modified web files.
- **SC-005**: All UI interactions (opening dialog, switching tabs, toggling mobile drawer) maintain 60 FPS transitions without visual jank or hydration mismatches.

---

## Assumptions

- Backend API endpoints (`GET/POST /api/v1/gateway/projects`, `GET /api/v1/gateway/projects/{id}`, `GET /api/v1/auth/me`) are operational and conform to [api.generated.d.ts](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/web/src/types/api.generated.d.ts).
- Users authenticate via DUT-AI SSO with valid session cookies or Bearer token stored via `auth-token.ts`.
- Component primitives (`Dialog`, `Button`, `Input`, `Card`, `Badge`, `Tabs`, `Skeleton`, `Sonner`) from `shadcn/ui` are available in `web/src/components/ui/`.
