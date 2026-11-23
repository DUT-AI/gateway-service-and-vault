# Feature Specification: Web Phase 5 - Upstream Services Management & System Polish (DoD)

**Feature Branch**: `011-web-upstream-services`  
**Created**: 2026-11-23  
**Status**: Ready for Planning  
**Input**: Phase 5 requirements from `docs/WEB_ROADMAP.md` ("Giai Đoạn 5: Quản Lý Upstream Services & Hoàn Thiện Trải Nghiệm (Polish & DoD) - Quản lý dịch vụ đối tác (OpenAI, Payment API,...) được Gateway bảo vệ, hoàn thiện giao diện tổng thể và kiểm thử đầu-cuối").

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upstream Services Directory (Priority: P1) 🎯 MVP

As a system administrator or DevOps engineer, I want a dedicated management directory at `/services` displaying all registered upstream partner services (OpenAI, Payment APIs, CRM integrations, etc.) protected by the Zero-Trust Gateway, so that I can monitor and govern all external destination endpoints from a single control pane.

**Why this priority**: Core catalog required for upstream service governance and proxying. Without upstream service registration, the gateway has no destination routes to protect or inject credentials into.

**Independent Test**: Navigate to `/services` via AppShell navigation -> Verify data table renders registered services with Name, Slug badge, Base URL (with link/copy button), Auth Type badge (`BEARER_TOKEN` / `API_KEY` / `BASIC_AUTH` / `NO_AUTH`), Timeout in seconds, and Active status. Use search filter to find services in real time.

**Acceptance Scenarios**:
1. **Given** an authenticated user navigating to `/services`, **When** the page mounts, **Then** the system queries `GET /api/v1/gateway/services` and renders the `ServicesTable`.
2. **Given** services displayed, **When** reviewing a service row, **Then** the table displays the service name, slug badge, base URL, auth type badge, timeout in seconds, and active status.
3. **Given** a user searching in the filter bar, **When** typing a service name, slug, or base URL, **Then** the table filters rows in real time.
4. **Given** zero registered services, **When** viewing the page, **Then** an informative empty state appears with an action button to "Khai báo dịch vụ đầu tiên".
5. **Given** a network fetching state, **When** data is loading, **Then** accessible skeleton rows are displayed.

---

### User Story 2 - Upstream Service Declaration & Credential Vaulting (Priority: P2)

As a security lead or system operator, I want to declare a new upstream service via a modal dialog with automatic Vietnamese slug generation, URL validation, authentication type selection, and raw credential input (which the backend encrypts at rest using AES-256-GCM), so that developer applications never handle or see real 3rd-party vendor credentials.

**Why this priority**: Enforces Constitution Principle VIII (Upstream Protection & Credential Injection). Downstream client applications only supply Virtual Keys; the gateway intercepts and injects the encrypted upstream credential transparently.

**Independent Test**: On `/services`, click "Khai báo dịch vụ mới" -> Enter name "OpenAI API Platform" -> Observe auto-generated slug `openai-api-platform` -> Enter Base URL `https://api.openai.com/v1` -> Select Auth Type `BEARER_TOKEN` -> Enter Credential `sk-proj-sample-token-123` -> Set Timeout `60` -> Submit -> Modal closes -> New service appears in the table with status `Đang hoạt động`.

**Acceptance Scenarios**:
1. **Given** the `/services` page, **When** clicking "Khai báo dịch vụ mới", **Then** the `CreateServiceDialog` opens with inputs for Service Name, Slug, Base URL, Auth Type, Credential, and Timeout Seconds.
2. **Given** typing a Vietnamese or English service name, **When** typing in the name field, **Then** the slug field auto-populates with a normalized kebab-case slug (e.g., "Cổng Thanh Toán VNPay" -> "cong-thanh-toan-vnpay") unless manually overridden.
3. **Given** invalid form inputs (e.g. invalid URL, missing name or credential), **When** submitting, **Then** client-side Zod validation prevents submission and displays contextual field errors.
4. **Given** valid inputs, **When** clicking "Lưu dịch vụ upstream", **Then** the system sends `POST /api/v1/gateway/services`, shows a pending loading spinner, and upon success refreshes the `["gateway", "services"]` cache, displays a Sonner success toast, and closes the dialog.
5. **Given** credential entry, **When** inputting the secret credential, **Then** the field is masked by default with an Eye/EyeOff toggle and includes a security note explaining that credentials are encrypted with AES-256-GCM and never displayed in plaintext again.

---

### User Story 3 - System Polish, Cross-Navigation & DoD Quality Gate (Priority: P3)

As an engineer or stakeholder, I want cohesive navigation across all 5 modules (Dashboard, Projects, Vault, Clients/mTLS, Services), uniform responsive design, fast page transitions, and passing build & test suites, so that the web application functions as a unified, enterprise-grade cloud control plane.

**Why this priority**: Fulfills the Definition of Done (DoD) from the Web Roadmap, ensuring production readiness with 0 errors across TypeScript, Next.js build, and backend test suites.

**Independent Test**: Navigate through `/dashboard` -> `/projects` -> `/projects/[id]` -> `/clients` -> `/services` -> Verify active menu states, responsive sidebar toggling, no console warnings, and verify `pnpm --prefix web typecheck`, `pnpm --prefix web build`, and `uv run pytest` pass cleanly.

**Acceptance Scenarios**:
1. **Given** any page in the application, **When** navigating between AppShell routes, **Then** the active sidebar navigation item accurately reflects the current route and page titles match.
2. **Given** all 5 modules, **When** running `pnpm --prefix web typecheck` and `pnpm --prefix web build`, **Then** build succeeds with zero errors and zero ESLint/TypeScript warnings.
3. **Given** backend tests, **When** running `uv run pytest`, **Then** 46/46 unit and integration tests pass with 100% clean architecture domain purity.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Domain 1: Upstream Services Catalog (`/services`)
- **FR-001**: System MUST provide a dedicated route `/services` accessible via the AppShell sidebar under "Dịch vụ hệ thống".
- **FR-002**: System MUST query `GET /api/v1/gateway/services` and render registered services in `ServicesTable` with columns: Tên & Slug, Base URL, Loại xác thực, Timeout, Trạng thái.
- **FR-003**: System MUST provide a search bar filtering services by name, slug, or base URL in real time.
- **FR-004**: System MUST render accessible skeleton rows during loading and a friendly empty state when no services are registered.

#### Domain 2: Service Declaration & Credential Vaulting
- **FR-005**: System MUST provide `CreateServiceDialog` with fields for Name, Slug, Base URL, Auth Type (`BEARER_TOKEN`, `API_KEY`, `BASIC_AUTH`, `NO_AUTH`), Credential, and Timeout Seconds.
- **FR-006**: System MUST automatically generate kebab-case URL slugs from service names with Vietnamese diacritic stripping.
- **FR-007**: System MUST validate form fields using Zod:
  - `name`: min 2, max 100 characters.
  - `slug`: min 2, max 100 characters, regex `/^[a-z0-9-]+$/`.
  - `base_url`: valid HTTP or HTTPS URL (regex `/^https?:\/\/.+/`).
  - `auth_type`: enum `"BEARER_TOKEN" | "API_KEY" | "BASIC_AUTH" | "NO_AUTH"`.
  - `credential`: min 1 character (required for authenticated services).
  - `timeout_seconds`: integer between 1 and 300 (default 30).
- **FR-008**: System MUST call `POST /api/v1/gateway/services` and handle pending mutation loading states.
- **FR-009**: System MUST invalidate TanStack Query key `["gateway", "services"]` upon successful creation and show a Sonner toast notification.

#### Domain 3: System Polish & Definition of Done
- **FR-010**: System MUST verify active route highlighting in `AppShell` for `/services`.
- **FR-011**: System MUST pass strict TypeScript validation (`tsc --noEmit`).
- **FR-012**: System MUST pass Next.js production build (`next build`).
- **FR-013**: System MUST maintain 100% pass rate on backend test suite (`pytest`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: Upstream service declaration and listing roundtrip completes in under **500ms**.
- **SC-002**: Search filtering updates the UI within **50ms**.
- **SC-003**: Zero plain-text credential leaks: raw upstream credentials are submitted directly to the backend for encryption and never cached or logged in browser storage.
- **SC-004**: 100% type safety and production build pass with zero errors.
- **SC-005**: All 5 phases of the Web Roadmap are fully delivered and verified end-to-end.
