# Implementation Plan: Developer Onboarding & Docker Machine Experience (Phase 4)

**Branch**: `016-developer-onboarding-docker-machine` | **Date**: 2026-11-23 | **Spec**: [specs/016-developer-onboarding-docker-machine/spec.md](file:///Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/specs/016-developer-onboarding-docker-machine/spec.md)

## Summary
Enhance developer onboarding, machine workload deployment, and SDK integration:
1. Verify and polish `CertDownloadDialog` ensuring single-click bundle download for `.crt` and `.key` with clean PEM formatting and toast feedback.
2. Build `DockerDeploymentGuideDialog` (`web/src/features/clients/components/docker-deployment-guide-dialog.tsx`) and link it via a "Hướng dẫn Docker Workload" button in `ClientsTable`.
3. Build `SdkQuickstartDialog` (`web/src/features/vault/components/sdk-quickstart-dialog.tsx`) with zero-.env in-memory loading snippets, and integrate a "Tích hợp SDK" button into `VaultView`.
4. Validate responsive design, accessibility, and static type safety.

## Technical Context
- **Frontend Framework**: Next.js 16 (App Router), React 19, TypeScript 5.6.
- **Styling**: Tailwind CSS v4, Lucide React icons, Radix UI Dialog.
- **SDK Target**: `packages/dut-vault-sdk` (Python 3.12+).
- **Quality Gates**: `pnpm tsc --noEmit` with 0 errors.

## Constitution Check
- **VI. Dynamic Vault & Zero .env Files**: SDK guide instructs developers on runtime memory injection (`DutVaultClient.load_into_environ()`) instead of writing plaintext `.env` files. (PASS)
- **VII. Real-Time In-Memory Hot-Reload**: Demonstrates SSE subscription and hot-reload event listener. (PASS)
- **VIII. Zero-Trust Identity Binding**: Guides Docker workloads to mount internal CA-signed client certificates and inject virtual keys. (PASS)

## Project Structure
```text
specs/016-developer-onboarding-docker-machine/
├── spec.md
├── plan.md
└── tasks.md
```

## Architecture & Implementation Steps

### Phase 1: Certificate Download Polish (Task 4.1)
- Verify `web/src/features/clients/components/cert-download-dialog.tsx` provides clean `.crt` and `.key` downloads, combined bundle download, and fingerprint copy.

### Phase 2: Docker Workload Guide (Task 4.2)
- Create `web/src/features/clients/components/docker-deployment-guide-dialog.tsx` featuring:
  - Step 1: Mounting certificates as read-only volume (`./certs/client.crt:/etc/ssl/certs/client.crt:ro`).
  - Step 2: `docker-compose.yml` snippet with `VIRTUAL_ACCESS_KEY` environment variable.
  - Step 3: Container mTLS cURL verification command.
- Add "Hướng dẫn Docker Workload" trigger button in `ClientsTable` toolbar.

### Phase 3: Vault SDK Quickstart Modal (Task 4.3)
- Create `web/src/features/vault/components/sdk-quickstart-dialog.tsx` featuring:
  - Installation: `pip install dut-vault-sdk`.
  - Python code snippet loading secrets dynamically into `os.environ` without `.env`.
  - Hot-reload callback registration snippet.
  - Tabbed language view (Python Async, Python Sync).
- Add "Tích hợp SDK" trigger button in `VaultView` action toolbar.

### Phase 4: Polish & Quality Gates
- Update `docs/CHECKLIST_REMAINING_TASKS.md`.
- Run frontend type check: `cd web && pnpm tsc --noEmit`.
