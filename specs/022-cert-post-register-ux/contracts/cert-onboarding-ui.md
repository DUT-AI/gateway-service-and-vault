# UI Component Contracts: Post-Registration Certificate Onboarding UX

**Feature**: `022-cert-post-register-ux`

## 1. `getClientCertFilenames(deviceName: string)`
Located in `web/src/features/clients/utils/download-file.ts`:
- **Input**: `deviceName: string`
- **Output**: `{ crtFilename: string; keyFilename: string }`
- **Rule**: `slug = deviceName.toLowerCase().replace(/[^a-z0-9]/g, "-")`, returning `${slug}-client.crt` and `${slug}-client.key`.

## 2. `CertInstallInstructions`
Located in `web/src/features/clients/components/cert-install-instructions.tsx`:
- **Props**:
  - `crtFilename: string`
  - `keyFilename: string`
  - `clientType: ClientType`
- **Behavior**:
  - Renders 3 environment tabs (`macOS / Linux`, `Windows`, `Docker`), defaulting to `"docker"` when `clientType === "APP_SERVER"` and `"unix"` otherwise.
  - Displays copyable command blocks placing/mounting the downloaded files into `~/.dut-vault/client.crt` & `~/.dut-vault/client.key` (with `chmod 600` on Unix) or Docker `./certs/` volume mounts.

## 3. `CertNextStepsCard`
Located in `web/src/features/clients/components/cert-next-steps-card.tsx`:
- **Props**:
  - `bundle: RegisterClientResult`
  - `isOtherRole: boolean`
  - `onNavigateToProjects: () => void`
  - `onOpenDockerGuide?: () => void`
- **Behavior**:
  - If `isOtherRole`: shows Regular Developer guidance + 1-click "Sao chép thông tin gửi Project Developer" (copies device name + SHA-256 fingerprint) + link to `/projects`.
  - If `!isOtherRole`: shows Project Developer / Admin guidance + link to `/projects` + optional "Xem hướng dẫn Docker Workload" button when `bundle.client_type === "APP_SERVER"`.
  - Includes a collapsible/compact quick verification command (`curl --cert ~/.dut-vault/client.crt --key ~/.dut-vault/client.key ...` / `dut-vault run`).

## 4. `CertDownloadDialog`
Located in `web/src/features/clients/components/cert-download-dialog.tsx`:
- **Props**:
  - `open: boolean`
  - `onOpenChange: (open: boolean) => void`
  - `bundle: RegisterClientResult | null`
- **Behavior**:
  - Resets local download flags cleanly via React `key={bundle?.id}` from parent or state reset on bundle change.
  - Guards all close paths (`onOpenChange(false)`, `X`, backdrop, footer button) when `!downloadedKey`.
