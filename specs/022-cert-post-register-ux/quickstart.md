# Quickstart Validation Guide: Post-Registration Certificate Onboarding UX

**Feature**: `022-cert-post-register-ux`

## Verification Steps

1. **TypeScript & ESLint**:
   ```bash
   cd web && pnpm typecheck && npx eslint src/features/clients/components/cert-download-dialog.tsx src/features/clients/components/cert-install-instructions.tsx src/features/clients/components/cert-next-steps-card.tsx src/features/clients/utils/download-file.ts
   ```
   - Expected: 0 TypeScript errors, 0 ESLint errors/warnings.

2. **Manual / Browser UX Verification**:
   - **As Regular Developer (`RoleTier.OTHER`)**:
     1. Register a `USER_DEVICE` named `"Test Dev 123"`.
     2. Confirm `CertDownloadDialog` shows 3 numbered steps.
     3. Click `X` before downloading `client.key` -> confirmation prompt warns that `client.key` is 1-time only.
     4. Click "Tải cả hai tệp" -> Step 1 shows checkmarks on both `client.crt` and `client.key`.
     5. In Step 2, verify `macOS / Linux` command uses `test-dev-123-client.crt` and `test-dev-123-client.key` and copies cleanly.
     6. In Step 3, verify Regular Developer instructions + "Sao chép thông tin gửi Project Developer" button work.
   - **As Project Developer (`APP_SERVER`)**:
     1. Register an `APP_SERVER`.
     2. Verify Step 2 defaults to `Docker` tab and Step 3 offers both "Tới Dự án" and "Hướng dẫn Docker Workload".
