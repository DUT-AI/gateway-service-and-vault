# Feature Specification: Developer Onboarding & Docker Machine Experience (Phase 4)

**Feature Branch**: `016-developer-onboarding-docker-machine`  
**Created**: 2026-11-23  
**Status**: Ready for Implementation  
**Input**: Giai đoạn 4: Developer Onboarding & Trải Nghiệm Docker Machine (Ưu tiên P3 - Medium)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Certificate & Private Key Bundle Download (Priority: P1) 🎯 MVP

As a Developer registering a new User Device or App Server, I want to download both my X.509 client certificate (`client.crt`) and private key (`client.key`) with a single click, and copy the SHA-256 fingerprint, so that I don't have to manually format or copy-paste PEM strings from dialog boxes.

**Why this priority**: Without seamless certificate file downloading, developers cannot configure mTLS on their local machines or Docker workloads.

**Independent Test**: Register a client; click "Tải trọn bộ chứng chỉ (.crt + .key)"; verify two valid PEM files are downloaded with correct extensions and content.

**Acceptance Scenarios**:
1. **Given** a newly registered client in `CertDownloadDialog`, **When** clicking "Tải trọn bộ chứng chỉ", **Then** both `<name>-client.crt` and `<name>-client.key` are triggered for browser download in PEM format.
2. **Given** the certificate modal, **When** clicking "Sao chép Fingerprint", **Then** the 64-character SHA-256 fingerprint is copied to clipboard with toast confirmation.

---

### User Story 2 - Docker Machine Identity Workload Guide (Priority: P2)

As a DevOps Engineer or Backend Developer deploying a service into Docker, I want an interactive guide modal explaining how to mount mTLS client certificates into a container and pass `VIRTUAL_ACCESS_KEY`, with copyable `docker-compose.yml` and `curl` snippets, so that I can configure my containerized app server in under 2 minutes.

**Why this priority**: Developers frequently struggle with mTLS certificate file mounting, paths, and environment variable configuration inside Docker containers.

**Independent Test**:
Click "Hướng dẫn Docker Workload" on the Clients page; verify modal opens with tabs for `docker-compose.yml`, `Dockerfile`, and `Test cURL command`; verify copying snippets copies valid syntax.

**Acceptance Scenarios**:
1. **Given** the Clients management page, **When** clicking "Hướng dẫn Docker Workload", **Then** `DockerDeploymentGuideDialog` opens with clear steps and volume mounting instructions.
2. **Given** the Docker guide modal, **When** switching to Docker Compose tab, **Then** a snippet with volume mounts for `/etc/ssl/certs/client.crt` and `/etc/ssl/private/client.key` and `VIRTUAL_ACCESS_KEY` is shown with a 1-click copy button.

---

### User Story 3 - In-Memory SDK Quickstart Modal in Vault (Priority: P2)

As a Developer working on a project using Dynamic Vault, I want a "Tích hợp SDK" guide modal inside the Vault view showing how to install `dut-vault-sdk` and load secrets directly into RAM without `.env` files, complete with live project ID and scopes pre-filled, so that I can integrate dynamic secret loading in seconds.

**Why this priority**: Fulfills Constitution Principle VI (Zero .env Files) and VII (In-Memory Hot-Reload), guiding developers to avoid storing secrets in disk `.env` files.

**Independent Test**:
In project Vault tab, click "Tích hợp SDK"; verify modal displays `pip install dut-vault-sdk`, pre-filled `project_id`, selected scope, code snippet using `DutVaultClient`, and explanation of in-memory hot-reload.

**Acceptance Scenarios**:
1. **Given** an open project Vault view, **When** clicking "Tích hợp SDK" on the action toolbar, **Then** `SdkQuickstartDialog` opens displaying code customized to the current project.
2. **Given** the SDK guide modal, **When** clicking copy code, **Then** executable Python code initializing `DutVaultClient` is copied to clipboard.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `CertDownloadDialog` MUST provide individual buttons for downloading `<name>-client.crt`, `<name>-client.key`, and a combined "Tải trọn bộ chứng chỉ" action.
- **FR-002**: Web UI MUST provide a `DockerDeploymentGuideDialog` in `web/src/features/clients/components/docker-deployment-guide-dialog.tsx`:
  - Step 1: Chuẩn bị thư mục chứa chứng chỉ (`./certs/`).
  - Step 2: Cấu hình `docker-compose.yml` với volume mount read-only (`:ro`).
  - Step 3: Kiểm tra kết nối mTLS qua Gateway bằng lệnh cURL mẫu.
  - One-click copy buttons for all code blocks.
- **FR-003**: `ClientsTable` MUST include a "Hướng dẫn Docker Workload" button in its top action bar.
- **FR-004**: Web UI MUST provide an `SdkQuickstartDialog` in `web/src/features/vault/components/sdk-quickstart-dialog.tsx`:
  - Quick install command: `pip install dut-vault-sdk`.
  - Python snippet loading secrets directly into process memory (`os.environ`).
  - Pre-fills current `projectId` and `projectName`.
  - Hot-reload callback snippet demonstrating `< 5s` zero-downtime rotation.
- **FR-005**: `VaultView` MUST include a "Tích hợp SDK" button in its header action bar alongside "Phân quyền truy cập".

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can download client mTLS certificates, copy a Docker Compose snippet, and initiate a containerized mTLS request in under 2 minutes.
- **SC-002**: A developer can open the SDK Quickstart modal, copy the Python snippet, and run a script loading secrets from Dynamic Vault without creating a `.env` file.
- **SC-003**: Frontend builds cleanly with zero TypeScript errors (`pnpm tsc --noEmit`).
