# Data Model: Post-Registration Certificate Onboarding UX

**Feature**: `022-cert-post-register-ux`

## Client-Side View Models & State

No backend database tables or API schemas are modified. All data comes from the existing `RegisterClientResult` payload and `useAuth()` context.

### `RegisterClientResult` (existing)
- `id: string`
- `name: string`
- `client_type: "USER_DEVICE" | "APP_SERVER"`
- `cert_pem: string`
- `key_pem: string`
- `cert_fingerprint: string`
- `cert_serial: string`
- `expires_at: string`

### `CertOnboardingState` (local UI state in `CertDownloadDialog`)
- `downloadedCrt: boolean` — `true` after user triggers `client.crt` download.
- `downloadedKey: boolean` — `true` after user triggers `client.key` download.
- `osTab: "unix" | "windows" | "docker"` — defaults to `"docker"` when `bundle.client_type === "APP_SERVER"`, otherwise `"unix"`.
- `dockerGuideOpen: boolean` — optional state to open `DockerDeploymentGuideDialog` directly from Step 3 for `APP_SERVER`.
