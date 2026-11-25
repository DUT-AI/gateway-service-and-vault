# Feature Specification: Post-Registration Certificate Onboarding UX

**Feature Branch**: `022-cert-post-register-ux`

**Created**: 2026-11-25

**Status**: Draft

**Input**: User description: "sau khi hoàn tất đăng ký, tôi muốn có 1 UX sao để thuận tiện cho người dùng nhất, biết là sẽ cần phải tải rồi, nhưng bước sau làm gì nữa?"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Guided Step-by-Step Post-Registration Flow (Priority: P1)

Immediately after registering an mTLS device (`USER_DEVICE` or `APP_SERVER`), the user sees a structured, step-by-step onboarding experience inside the post-registration modal (`CertDownloadDialog`) instead of a flat download form with a vague one-line hint. The modal guides the user through:
1. **Step 1 — Download Certificates**: Download `client.crt` & `client.key` (with live completion state showing checkmarks once downloaded).
2. **Step 2 — Place & Secure Files on Machine**: Provide ready-to-copy shell commands (with OS/environment tabs: **macOS / Linux**, **Windows PowerShell**, or **Docker**) that move the downloaded files into `~/.dut-vault/` (or `/etc/ssl/...` for Docker) and apply strict file permissions (`chmod 600` on `client.key`).
3. **Step 3 — Next Action Based on Role & Client Type**:
   - **Regular Developer (`RoleTier.OTHER`)**: Clearly inform them that their device is now ready to be bound, and instruct them to notify their **Project Developer** (providing a 1-click copyable summary message containing device name + SHA-256 fingerprint) so the Project Developer can issue a Virtual Key for the device in the project's **Virtual Keys** tab, plus a button to view their projects.
   - **Project Developer / Admin (`RoleTier.PROJECT_DEVELOPER` / `RoleTier.ADMIN`)**: Provide a direct action to go to `/projects` (tab **Virtual Keys**) to issue a Virtual Key for the newly registered device, or open the **Docker Workload Guide** if `client_type === "APP_SERVER"`.

**Why this priority**: Currently, users see "Hãy tải ngay cả hai tệp... chuyển vào `~/.dut-vault/`" and "Bước tiếp theo: Vào tab Virtual Keys...", which leaves them guessing exact file paths, permissions, and—for Regular Developers—why they cannot create a Virtual Key themselves. Guided, role-aware instructions eliminate setup friction and support requests.

**Independent Test**: Register a device as a Regular Developer (`USER_DEVICE`) and as a Project Developer (`USER_DEVICE` and `APP_SERVER`), and verify that the modal displays the 3-step checklist, live download progress, 1-click copyable setup commands, and role/client-type-specific next-step actions.

**Acceptance Scenarios**:

1. **Given** a user completes device registration, **When** `CertDownloadDialog` opens, **Then** Step 1 highlights downloading `client.crt` & `client.key` (and marks Step 1 complete once both files are downloaded).
2. **Given** a user is on Step 2, **When** they switch between `macOS / Linux`, `Windows`, and `Docker` tabs, **Then** they see exact, copyable commands referencing the actual downloaded filenames (`<slug>-client.crt`, `<slug>-client.key`) and target `~/.dut-vault/client.crt` & `~/.dut-vault/client.key` with `chmod 600`.
3. **Given** the authenticated user is a **Regular Developer (`isOtherRole`)**, **When** they view Step 3, **Then** the UI explains that their Project Developer will issue a Virtual Key for this device, provides a 1-click "Sao chép thông tin gửi Project Developer" button (copying device name + fingerprint), and links to `/projects`.
4. **Given** the authenticated user is a **Project Developer or Admin**, **When** they view Step 3 for a `USER_DEVICE`, **Then** the UI provides a direct CTA to `/projects` to generate a Virtual Key; for an `APP_SERVER`, it also offers a button to open the Docker Workload deployment guide.

---

### User Story 2 - Safe Dismissal & Zero-Loss Guardrails (Priority: P2)

Prevent users from accidentally losing their one-time `client.key` before saving it, while allowing intentional dismissal without friction once downloaded.

**Why this priority**: Because the Private Key (`client.key`) is never stored on the server, closing the modal before downloading forces the user to revoke and re-register a new device.

**Independent Test**: Attempt to close the dialog via the `X` button, backdrop click, or footer button before downloading `client.key` and verify a non-destructive confirmation/warning prevents accidental loss; after downloading both files, verify the primary footer button transitions cleanly to "Hoàn tất" without nagging.

**Acceptance Scenarios**:

1. **Given** the user has NOT downloaded `client.key`, **When** they click "Đóng" or press Escape / click `X`, **Then** the dialog warns them clearly that `client.key` cannot be recovered after closing and requires explicit confirmation.
2. **Given** the user HAS downloaded both `client.crt` and `client.key`, **When** they click "Hoàn tất" or "Tới Dự án", **Then** the modal closes immediately with zero confirmation prompt.

---

### User Story 3 - Quick SDK Verification Snippet (Priority: P3)

Help developers verify that their local certificate setup works immediately without waiting until they have already debugged a failing gateway call.

**Why this priority**: Giving a concise 1-command / minimal SDK snippet closes the loop between downloading certs and running code.

**Independent Test**: Expand/view the verification snippet in Step 3 and verify it references `~/.dut-vault/client.crt`, `~/.dut-vault/client.key`, and `X-Virtual-Key`.

**Acceptance Scenarios**:

1. **Given** a user is in Step 3 of `CertDownloadDialog`, **When** they view the quick-check snippet, **Then** they see how `dut-vault-sdk` (or `curl --cert ~/.dut-vault/client.crt --key ~/.dut-vault/client.key`) consumes the saved files once a Virtual Key is issued.

---

### Edge Cases

- What happens when the user's device name contains spaces or Vietnamese accents (e.g., `"Máy tính cá nhân 123"`)? The copyable `mv` / `Copy-Item` commands MUST use the exact sanitized filename produced by `handleDownloadCrt` / `handleDownloadKey` (`<slug>-client.crt`, `<slug>-client.key`) so copying and pasting the command works without manual editing.
- What happens if the user closes via `X` or clicking outside the dialog (`onOpenChange(false)`) before downloading `client.key`? Intercept `onOpenChange` with the same `downloadedKey` check as `handleFinish` so clicking `X` or outside doesn't silently discard the private key.
- What happens if a Project Developer registers an `APP_SERVER`? Step 2 defaults to the `Docker` tab (or highlights Docker volume mount instructions) and Step 3 includes a button to open `DockerDeploymentGuideDialog`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `CertDownloadDialog` MUST display a clear numbered 3-step onboarding progression: (1) Tải chứng chỉ & khóa riêng, (2) Cài đặt vào thư mục an toàn trên máy, (3) Cấp / nhận Virtual Key và kết nối.
- **FR-002**: Step 1 MUST track `downloadedCrt` and `downloadedKey` states and visually indicate completion once both files are downloaded.
- **FR-003**: Step 2 MUST provide tabbed, 1-click copyable setup commands for `macOS / Linux`, `Windows`, and `Docker`, dynamically interpolating the exact downloaded filenames (`<slug>-client.crt` and `<slug>-client.key`) and setting restrictive permissions (`chmod 600 ~/.dut-vault/client.key`).
- **FR-004**: Step 3 MUST adapt its guidance and CTA based on `useAuth().isOtherRole` and `bundle.client_type`:
  - If `isOtherRole`: explain that the Project Developer needs to bind a Virtual Key to this device in the project's **Virtual Keys** tab, provide a 1-click copyable handoff message (device name + SHA-256 fingerprint), and provide a link to `/projects`.
  - If `!isOtherRole`: provide a direct link to `/projects` to create a Virtual Key, and if `client_type === "APP_SERVER"`, offer a button to open `DockerDeploymentGuideDialog`.
- **FR-005**: Closing the modal via any trigger (`X`, backdrop click, Escape, or footer button) MUST guard against accidental loss when `downloadedKey` is `false`.
- **FR-006**: `CertDownloadDialog` MUST remain modular (extracting subcomponents such as `cert-install-instructions.tsx` if needed) and pass `pnpm typecheck` and `eslint` with zero errors.

### Key Entities *(include if feature involves data)*

- **RegisterClientResult**: Existing response payload returned on `POST /api/v1/gateway/clients` containing `id`, `name`, `client_type`, `cert_pem`, `key_pem`, `cert_fingerprint`, `cert_serial`, and `expires_at` (no backend schema changes required).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete certificate download and local placement into `~/.dut-vault/` in under 30 seconds using the 1-click download and copyable OS-specific command.
- **SC-002**: 100% of dismissal paths (`X`, backdrop, Escape, footer button) prevent accidental loss of `client.key` prior to download.
- **SC-003**: Both Regular Developers (`RoleTier.OTHER`) and Project Developers/Admins (`RoleTier.PROJECT_DEVELOPER` / `ADMIN`) receive role-accurate next-step instructions with zero dead-end CTAs.

## Assumptions

- No backend API changes are needed; all required metadata (`name`, `client_type`, `cert_fingerprint`, `cert_pem`, `key_pem`) is already present in `RegisterClientResult`.
- The default local mTLS certificate directory convention for `dut-vault-sdk` and CLI is `~/.dut-vault/client.crt` and `~/.dut-vault/client.key`.
- `CertDownloadDialog` already has `useAuth()` available in the client context to distinguish `isOtherRole` vs `PROJECT_DEVELOPER`/`ADMIN`.
