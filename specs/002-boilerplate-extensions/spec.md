# Feature Specification: Boilerplate Advanced Capabilities (DUT-AI Style)

**Feature Branch**: `002-boilerplate-extensions`

**Created**: 2026-11-22

**Status**: Draft

**Input**: User request: "Kế thừa những cái sau: OutboxProcessor, Frontend Next.js Feature-First & Auth Context, Pagination Abstraction, Multi-Stage Dockerfile & CI/CD Pipeline"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Full-Stack Authentication & Protected Dashboard (Priority: P1)

As a web user, I want to access a login/register interface, submit my credentials, be authenticated via secure cookies or tokens, and be redirected into a protected dashboard where my profile is displayed, so that unauthenticated visitors are automatically kept out of protected areas.

**Why this priority**: Connects the backend API directly to the frontend user experience, providing a complete working full-stack template out-of-the-box.

**Independent Test**: Can be tested by navigating to `/login`, entering credentials, observing automatic redirect to `/dashboard` upon success, and attempting to directly visit `/dashboard` when logged out to verify redirection back to `/login`.

**Acceptance Scenarios**:

1. **Given** an unauthenticated visitor, **When** they attempt to visit `/dashboard`, **Then** the application intercepts the request and redirects them to `/login`.
2. **Given** valid credentials entered on `/login`, **When** the user clicks Submit, **Then** the `auth-context` stores the user state, updates TanStack Query cache, and redirects the user to `/dashboard`.
3. **Given** an authenticated user on `/dashboard`, **When** they click "Logout", **Then** the session is cleared, credentials are deleted, and the user is redirected to `/login`.

---

### User Story 2 - Standardized Pagination, Filtering, and Search (Priority: P1)

As a backend and frontend developer, I want all list queries across all modules to follow a unified pagination contract (`page`, `page_size`, `total`, `items`, `total_pages`), so that I don't have to redesign pagination logic for each new entity.

**Why this priority**: Reusable data access pattern required by virtually every business feature in enterprise applications.

**Independent Test**: Can be tested by querying `/api/v1/auth/users?page=1&page_size=10` and verifying the JSON response conforms to `PaginatedResponse` structure with correct count and item slices.

**Acceptance Scenarios**:

1. **Given** a collection of records in the database, **When** a client requests page 1 with page size 10, **Then** the system returns exactly up to 10 items, the total count, current page, and calculated total pages.
2. **Given** a search query parameter `search=alice`, **When** the list endpoint executes, **Then** only matching records are returned and the total count reflects the filtered subset.

---

### User Story 3 - Background Outbox Event Dispatcher (Priority: P2)

As a backend engineer, I want an `OutboxProcessor` that scans pending domain events from the database, executes registered handlers, and tracks failure states, so that background workflows run reliably without losing events.

**Why this priority**: Guarantees at-least-once event delivery for critical asynchronous actions (e.g. notifications, webhook calls, cache invalidation).

**Independent Test**: Can be tested by inserting an outbox event, invoking `OutboxProcessor.process_pending_batch()`, and confirming the registered handler executes and the event status changes to `PROCESSED`.

**Acceptance Scenarios**:

1. **Given** a pending outbox event with a registered handler, **When** the processor executes, **Then** the handler receives the payload, the event is marked `PROCESSED`, and `processed_at` timestamp is recorded.
2. **Given** a handler that raises an unexpected exception, **When** the processor executes, **Then** the event is marked `FAILED` with error message captured and `retry_count` incremented.

---

### User Story 4 - Multi-Stage Docker Builds & Automated CI/CD (Priority: P2)

As a DevOps engineer, I want production-ready multi-stage Dockerfiles and a GitHub Actions workflow, so that code is automatically linted, tested, and checked for API schema drift on every pull request.

**Why this priority**: Guarantees deployment readiness, prevents broken commits, and ensures frontend types never diverge from backend DTOs.

**Independent Test**: Can be tested by running `docker build -t app-backend .` and running the GitHub Actions verification commands locally.

**Acceptance Scenarios**:

1. **Given** a production Docker build, **When** the build completes, **Then** the resulting image runs as a non-root user, contains only production dependencies, and boots the FastAPI server cleanly.
2. **Given** a git repository with modified DTOs, **When** CI executes, **Then** it validates that `web/src/types/api.generated.d.ts` matches backend schemas or fails the build if drift occurs.

---

### Edge Cases

- **Token Expiry during User Session**: When a user's access token expires while browsing the web client, the Axios interceptor must detect the 401 response and redirect cleanly to `/login` without looping.
- **Outbox Handler Crash**: If a background event handler fails midway, the database transaction must record the failure details without crashing the entire worker process.
- **Negative or Zero Page Number**: When `page <= 0` or `page_size <= 0` is requested, validation must reject the request with HTTP 422 rather than causing database SQL errors.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an Axios API client in `web/src/lib/api.ts` with `withCredentials: true` and response interceptor redirecting to `/login` on unauthorized responses.
- **FR-002**: System MUST provide an `AuthProvider` and `useAuth()` hook in `web/src/contexts/auth-context.tsx` managing `user`, `isLoading`, `login`, `register`, and `logout` state.
- **FR-003**: System MUST structure frontend authentication in `web/src/features/auth/` containing `components/`, `hooks/`, `services/`, and `types/` with `react-hook-form` and `zod` validation.
- **FR-004**: System MUST provide a protected route layout in `web/src/app/(protected)/layout.tsx` guarding child routes and rendering a Dashboard page in `web/src/app/(protected)/dashboard/page.tsx`.
- **FR-005**: System MUST provide generic pagination schemas `PaginationParams` and `PaginatedResponse[T]` in `core/pagination/`.
- **FR-006**: System MUST provide a reusable SQLAlchemy query pagination helper in `core/pagination/helpers.py`.
- **FR-007**: System MUST provide a paginated list endpoint `GET /api/v1/auth/users` demonstrating the pagination pattern end-to-end.
- **FR-008**: System MUST implement `OutboxProcessor` in `core/events/processor.py` supporting handler registration, batch dispatching, and failure status updates.
- **FR-009**: System MUST provide a production multi-stage `Dockerfile` using `uv` with non-root security execution.
- **FR-010**: System MUST provide a GitHub Actions CI workflow in `.github/workflows/ci.yml` verifying linting, type-checking, test execution, and API contract drift detection.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete login on `/login` and see their dashboard in under 2 seconds.
- **SC-002**: Paginated list queries execute and return results in under 50ms for standard dataset sizes.
- **SC-003**: Outbox event processor handles up to 50 events per batch with zero lost transactions.
- **SC-004**: Production Docker container image builds in under 2 minutes and has an image size under 250MB.
- **SC-005**: CI workflow runs and completes all checks (linter, types, tests, API drift) in under 3 minutes.

## Assumptions

- Frontend runs Next.js 16 with App Router and TanStack Query v5.
- Docker engine and GitHub Actions are available for build and deployment pipelines.
