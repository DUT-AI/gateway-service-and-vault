# Research: Post-Registration Certificate Onboarding UX

**Feature**: `022-cert-post-register-ux`
**Date**: 2026-11-25

## Decisions & Rationale

### 1. Component Decomposition Strategy
- **Decision**: Decompose `CertDownloadDialog` into focused, single-purpose components under `web/src/features/clients/components/`:
  - `cert-download-dialog.tsx`: Dialog shell, download state tracking (`downloadedCrt`, `downloadedKey`), dismissal guardrail (`handleDismissAttempt`), and 3-step layout orchestration.
  - `cert-install-instructions.tsx`: Step 2 tabbed OS/environment setup instructions (`macOS / Linux`, `Windows`, `Docker`) with dynamic sanitized filenames and 1-click copy buttons.
  - `cert-next-steps-card.tsx`: Step 3 role-aware & client-type-aware next actions (`isOtherRole` handoff message vs Project Developer/Admin `/projects` CTA + `APP_SERVER` Docker guide trigger + quick verification snippet).
- **Rationale**: Keeps each file under ~200 lines, avoids creating a new God component, and matches the modular pattern established across `clients-table.tsx`, `secret-dialog.tsx`, and `generate-key-modal.tsx`.
- **Alternatives considered**: Keeping everything inside `cert-download-dialog.tsx` (~450+ lines) — rejected because it violates component modularity.

### 2. Filename Sanitization Consistency
- **Decision**: Extract a pure helper `getClientCertFilenames(deviceName: string)` (or colocate in `web/src/features/clients/utils/download-file.ts`) returning `{ crtFilename, keyFilename }` using the exact same sanitization logic (`name.toLowerCase().replace(/[^a-z0-9]/g, "-")`).
- **Rationale**: Guarantees the downloaded filename and the `mv` / `Copy-Item` / Docker volume commands in Step 2 always match character-for-character, even when `deviceName` contains spaces or Vietnamese diacritics.
- **Alternatives considered**: Duplicating `.replace(...)` in two components — rejected to avoid drift.

### 3. Safe Dismissal Guardrail Across All Close Triggers
- **Decision**: Intercept `Dialog`'s `onOpenChange(nextOpen)` so any close attempt (`X` button, backdrop click, `Escape`, or footer button) while `!downloadedKey` triggers confirmation before closing.
- **Rationale**: Currently `onOpenChange={onOpenChange}` bypasses `handleFinish`'s `downloadedKey` check when clicking `X` or the backdrop, risking accidental permanent loss of the one-time Private Key.
- **Alternatives considered**: Only checking on the footer button — rejected because users frequently click `X` or `Esc`.

### 4. Role-Aware Next Steps (`useAuth().isOtherRole`)
- **Decision**: Read `isOtherRole` from `useAuth()` inside `CertNextStepsCard`:
  - When `isOtherRole === true`: Explain that a Project Developer must issue the Virtual Key for this device in the project's **Virtual Keys** tab, and offer a 1-click copyable handoff message containing `bundle.name` and `bundle.cert_fingerprint`.
  - When `isOtherRole === false`: Direct CTA to `/projects` (Virtual Keys tab), plus an optional button to open `DockerDeploymentGuideDialog` when `bundle.client_type === "APP_SERVER"`.
- **Rationale**: Directly aligns with `021-dev-device-project-binding` 3-tier RBAC rules where Regular Developers cannot generate Virtual Keys themselves.
- **Alternatives considered**: Showing the same "Vào tab Virtual Keys để cấp API Key" message to everyone — rejected because it misleads Regular Developers into looking for a button they do not have.
