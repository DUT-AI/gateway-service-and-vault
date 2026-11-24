# Tasks: Pure SSO Authentication & Gateway Flow

**Input**: Design documents from `/specs/018-pure-sso-gateway-auth/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/sso-auth-api.yaml](contracts/sso-auth-api.yaml), [quickstart.md](quickstart.md)

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2], [US3], [US4])
- File paths are exact repository paths

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify development environment, network bindings, and current gateway/web configurations.

- [X] T001 Inspect APISIX route configurations and web API base URL settings in `modules/gateway/client/apisix_client.py` and `web/.env.local`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core gateway infrastructure updates that MUST be complete before ANY user story can function without CORS errors.

**⚠️ CRITICAL**: No browser network request can succeed through the gateway proxy until APISIX resolves preflight `OPTIONS` requests at the edge.

- [X] T002 [P] Configure APISIX native `cors` plugin on `control_plane_backend_route` (`/api/*`) in `modules/gateway/client/apisix_client.py` with `allow_origins="http://localhost:3000,http://127.0.0.1:3000,https://*.dutai.io.vn"`, `allow_methods="GET,POST,PUT,DELETE,PATCH,OPTIONS"`, `allow_headers="*,Authorization,Content-Type,X-Virtual-Key,X-Project-Id"`, `allow_credential=True`, and `max_age=3600`
- [X] T003 Resync APISIX control plane route via `ApisixAdminClient.sync_control_plane_route()` in `modules/gateway/client/apisix_client.py` to persist CORS plugin configuration in etcd

**Checkpoint**: Gateway foundation ready — browser preflight `OPTIONS` requests return `200 OK` at the edge in <2ms.

---

## Phase 3: User Story 2 - Gateway-Level CORS Preflight & Transparent Routing (Priority: P1)

**Goal**: As a frontend web client executing cross-origin requests against the API Gateway (`http://localhost:9080`), all preflight `OPTIONS` calls resolve with standard CORS headers so client-side network calls never fail with `Network Error` or `405 Method Not Allowed`.

**Independent Test**: Send `curl -i -X OPTIONS http://localhost:9080/api/v1/auth/sso-login -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: POST"`; Gateway returns `HTTP/1.1 200 OK` with `Access-Control-Allow-Origin: http://localhost:3000` and `Access-Control-Allow-Credentials: true`.

- [X] T004 [P] [US2] Implement integration test verifying APISIX route CORS preflight handling and response headers in `tests/integration/test_gateway_cors.py`
- [X] T005 [US2] Verify header transparency and upstream cookie/authorization forwarding through APISIX proxy in `modules/gateway/client/apisix_client.py`

**Checkpoint**: User Story 2 complete and independently verifiable via curl and test suite.

---

## Phase 4: User Story 1 - Seamless SSO Login & Immediate Dashboard Redirection (Priority: P1) 🎯 MVP

**Goal**: As an authenticated organization user with a central DUT-AI account, log into the platform using SSO credentials, obtain session tokens, and immediately land on the dashboard without network errors or false failure alerts.

**Independent Test**: Submit valid credentials on `http://localhost:3000/login`; system validates credentials via DUT-AI Manage IdP, stores session token in `localStorage` and `document.cookie`, and redirects to `/dashboard` within 2 seconds.

- [X] T006 [P] [US1] Validate `UserLoginRequest` (`email: EmailStr` required, `password: str` required) and `TokenResponse` (`access_token: str` required, `token_type: str = "bearer"` required, `expires_in: int` required) contract conformity in `apps/api/routers/auth_router.py`
- [X] T007 [P] [US1] Update `authService.login()` in `web/src/features/auth/services/auth-service.ts` to persist `access_token` under key `"project_boilerplate_token"` in `localStorage` and set `access_token` cookie with `path=/; SameSite=Lax` for Edge Middleware
- [X] T008 [US1] Refactor `useLoginMutation` in `web/src/features/auth/hooks/use-auth-queries.ts` to decouple credential validation from profile hydration, immediately executing `window.location.assign("/dashboard")` on successful token receipt
- [X] T009 [US1] Validate Edge session route guarding in `web/src/middleware.ts` to allow authenticated users with `access_token` cookie seamless access to protected routes

**Checkpoint**: User Story 1 (MVP) fully functional — users can log in cleanly and land on the dashboard.

---

## Phase 5: User Story 3 - Resilient Profile Hydration & Session Guarding (Priority: P2)

**Goal**: Retrieve authenticated user profile (`id: int`, `email: str`, `name: str | None`, `role: str`, `avatar_url: str | None`, `status: str`, `role_names: list[str]`, `permissions: list[str]`) from central directory with Redis caching (TTL 300s) and fail-open resilience.

**Independent Test**: Land on `/dashboard`, verify `GET /api/v1/auth/me` populates user details and permissions, and subsequent requests hit Redis cache without re-querying the remote IdP.

- [X] T010 [P] [US3] Add unit tests for Redis user profile caching (`identity:users:detail:{user_id}`) and fail-open behavior in `tests/unit/test_external_user_service.py`
- [X] T011 [US3] Enhance `useUserQuery` in `web/src/features/auth/hooks/use-auth-queries.ts` to handle loading states smoothly during dashboard mount with resilient query retry configuration
- [X] T012 [US3] Verify protected dashboard layout in `web/src/app/(protected)/layout.tsx` displays user identity badges and gracefully redirects to `/login` upon 401 session expiration

**Checkpoint**: User Story 3 complete — profile loads smoothly on dashboard with Redis caching.

---

## Phase 6: User Story 4 - Clear and Accurate Error Communication (Priority: P3)

**Goal**: Provide distinct, actionable error feedback distinguishing invalid credentials from network unreachable errors or server timeouts.

**Independent Test**: Enter invalid credentials on `/login`, verify error message states "Email hoặc mật khẩu SSO không chính xác", and verify network disconnection displays connectivity advice.

- [X] T013 [P] [US4] Configure Axios response error interceptor in `web/src/lib/api.ts` to normalize backend error details (`response.data.detail` or `response.data.message`)
- [X] T014 [US4] Update error display banner in `web/src/features/auth/components/login-form.tsx` to show specific error messages for 401 Unauthorized vs Network Error vs 500 Server Error

**Checkpoint**: User Story 4 complete — clear feedback provided on all error states.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end verification, linting, and quality gates across backend and frontend.

- [X] T015 [P] Run full backend test suite with `uv run pytest`
- [X] T016 [P] Run frontend TypeScript type checking and linting with `cd web && pnpm typecheck && pnpm lint`
- [X] T017 Execute end-to-end verification scenarios per [quickstart.md](quickstart.md) confirming preflight 200 OK and browser login redirection

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 — **BLOCKS all user stories** (gateway CORS must be live).
- **User Story 2 (Phase 3 - CORS Gateway)**: Validates gateway edge behavior.
- **User Story 1 (Phase 4 - SSO Login MVP)**: Depends on Phase 2 & 3. Delivers MVP login and redirect.
- **User Story 3 (Phase 5 - Profile Hydration)**: Depends on Phase 4 (authenticated session).
- **User Story 4 (Phase 6 - Error Handling)**: Can run in parallel with or after Phase 4.
- **Polish (Phase 7)**: Depends on all user story implementations being complete.

### User Story Dependencies

```text
[Phase 1: Setup] ──► [Phase 2: Foundational CORS Config]
                              │
                              ▼
                 [Phase 3: US2 - Gateway CORS (P1)]
                              │
                              ▼
                 [Phase 4: US1 - SSO Login & Redirect (P1) - MVP]
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
 [Phase 5: US3 - Profile (P2)]   [Phase 6: US4 - Error UX (P3)]
              │                               │
              └───────────────┬───────────────┘
                              ▼
                 [Phase 7: Polish & Verification]
```

### Parallel Execution Examples

#### Parallel Foundational & Backend Tasks:
```bash
# Can be executed in parallel:
Task T002: "Configure APISIX native cors plugin in modules/gateway/client/apisix_client.py"
Task T006: "Validate UserLoginRequest and TokenResponse in apps/api/routers/auth_router.py"
```

#### Parallel Frontend Tasks:
```bash
# Can be executed in parallel once T002/T003 are live:
Task T007: "Update authService.login() in web/src/features/auth/services/auth-service.ts"
Task T013: "Configure Axios response error interceptor in web/src/lib/api.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 & 2)
1. Complete Phase 1 (Setup) and Phase 2 (Foundational CORS in APISIX).
2. Validate Phase 3 (US2: Gateway Preflight returns 200 OK).
3. Complete Phase 4 (US1: SSO Login & Instant Redirection).
4. **STOP and VALIDATE**: Verify login on `http://localhost:3000/login` works smoothly and lands on `/dashboard`.

### Incremental Delivery
1. Foundation & Gateway CORS live → Zero browser `Network Error`.
2. SSO Login & Redirection live → Users can authenticate (MVP).
3. Profile hydration & Redis cache live → Dashboard shows identity and roles fast.
4. Error handling refinement live → Edge-case user feedback is clear.
5. All verification gates passed → Feature branch ready for merge.
