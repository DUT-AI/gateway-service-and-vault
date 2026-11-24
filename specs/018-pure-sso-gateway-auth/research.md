# Phase 0 Research: Pure SSO Authentication & Gateway Flow

## Research Topic 1: APISIX CORS Preflight Handling on Control Plane Routes

### Problem
When the browser on `http://localhost:3000` sends cross-origin requests to APISIX gateway on `http://localhost:9080/api/v1/auth/sso-login`, the browser triggers a CORS preflight (`OPTIONS`) request. Currently, if APISIX forwards the `OPTIONS` request to the backend or does not intercept it with the `cors` plugin, the client receives `405 Method Not Allowed`, causing Axios in the browser to throw `Network Error` before the actual POST request is ever sent.

### Decision
Attach the native APISIX `cors` plugin directly to the `control_plane_backend_route` (`/api/*`) in `ApisixAdminClient.sync_control_plane_route()`.

```json
{
  "plugins": {
    "cors": {
      "allow_origins": "http://localhost:3000,http://127.0.0.1:3000,https://*.dutai.io.vn",
      "allow_methods": "GET,POST,PUT,DELETE,PATCH,OPTIONS",
      "allow_headers": "*,Authorization,Content-Type,X-Virtual-Key,X-Project-Id",
      "allow_credential": true,
      "max_age": 3600
    }
  }
}
```

### Rationale
- **Edge Interception**: APISIX intercepts preflight `OPTIONS` requests directly at the proxy layer in <1ms without forwarding preflight calls to Python Uvicorn.
- **Eliminates 405 Method Not Allowed**: Preflight requests automatically receive `200 OK` with complete `Access-Control-Allow-*` headers.
- **Consistency**: Centralizes CORS policy at the API Gateway boundary rather than relying on disparate framework middlewares.

### Alternatives Considered
- *FastAPI CORS Middleware alone*: When requests route through reverse proxies, proxy configurations or regex route matchers often swallow or mutate OPTIONS headers before reaching ASGI handlers.
- *Nginx sidecar*: Redundant complexity since APISIX already provides a built-in high-performance Lua `cors` plugin.

---

## Research Topic 2: Session Persistence across Cross-Origin Ports (Port 3000 vs 9080)

### Problem
During local development, Next.js frontend runs on `http://localhost:3000` while APISIX gateway runs on `http://localhost:9080`. HttpOnly cookies set by `localhost:9080` without matching domain flags are subject to cross-port isolation in certain browsers, and Next.js Edge Middleware cannot access `localStorage`.

### Decision
Adopt a dual-channel token persistence strategy:
1. **Client Storage (`localStorage`)**: `authService.login` persists `access_token` under key `project_boilerplate_token`. Axios client interceptor automatically attaches `Authorization: Bearer <token>` to all HTTP calls.
2. **Client Cookie (`document.cookie`)**: `authService.login` immediately sets `access_token=<token>; path=/; SameSite=Lax` on `localhost:3000` so Next.js Edge Middleware (`middleware.ts`) can validate the session before rendering protected layouts.

### Rationale
- Guarantees 100% token availability for both client-side Axios requests and server-side Next.js route middleware.
- Completely eliminates cookie domain mismatch rejections across different development ports.

---

## Research Topic 3: Uncoupling Login Redirection from Profile Hydration

### Problem
Previously, `useLoginMutation.onSuccess` awaited `authService.getMe()` before redirecting. If `getMe()` took too long or encountered a network race, `onSuccess` threw an exception, making TanStack Query treat the entire login as failed, trapping the user on the login screen with a misleading error even after the backend returned `200 OK`.

### Decision
Uncouple credential validation from profile hydration:
1. `authService.login()` validates credentials and stores the token.
2. `useLoginMutation.onSuccess` invalidates `AUTH_QUERY_KEY` and immediately redirects to `/dashboard` via `window.location.assign("/dashboard")`.
3. `ProtectedLayout` on `/dashboard` activates `useUserQuery()` to fetch user profile, displaying a clean loading indicator and handling any transient directory retries gracefully.

### Rationale
- Follows the Single Responsibility Principle: the login mutation's sole job is authenticating credentials and establishing the session.
- Profile hydration belongs to the dashboard layout lifecycle, protecting users from false authentication rejections.
