# Feature Specification: Web Phase 4 - mTLS Device Management & Virtual Keys (Zero-Trust Gatekeeper)

**Feature Branch**: `010-web-mtls-virtual-keys`  
**Created**: 2026-11-23  
**Status**: Ready for Planning  
**Input**: Phase 4 requirements from `docs/WEB_ROADMAP.md` ("Giai Đoạn 4: Quản Lý Thiết Bị mTLS & Cấp Phát Virtual Keys (Zero-Trust Gatekeeper) - Cấp phát chứng chỉ mTLS cho Developer PC và Docker Server; sinh Virtual Access Key ràng buộc 1:1 chống rò rỉ").

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - mTLS Client & Device Directory (Priority: P1) 🎯 MVP

As a security engineer or system administrator, I want a dedicated management directory (`/clients`) showing all registered developer machines and server workloads, their cryptographic SHA-256 certificate fingerprints, and validity status, so that I can audit and govern all hardware/container identities accessing our platform.

**Why this priority**: Serves as the device inventory anchor for the Zero-Trust Gatekeeper. Without registered clients, no Virtual Access Keys can be bound.

**Independent Test**: Click "Thiết bị & Client" in AppShell navigation -> Verify routing to `/clients` -> View data table listing all registered client identities with Name, Type badge (`USER_DEVICE` / `APP_SERVER`), Fingerprint, Expiration date, and Active status.

**Acceptance Scenarios**:
1. **Given** an authenticated user navigating to `/clients`, **When** the page mounts, **Then** the system queries `GET /api/v1/gateway/clients` and renders the `ClientsTable`.
2. **Given** client records displayed, **When** reviewing a client row, **Then** the table displays the client name, type badge (`Developer PC` for `USER_DEVICE`, `Workload Server` for `APP_SERVER`), formatted expiration date, and truncated SHA-256 certificate fingerprint.
3. **Given** a user searching in the filter bar, **When** typing a device name or fingerprint snippet, **Then** the table filters rows in real time.
4. **Given** zero registered clients, **When** viewing the page, **Then** an informative empty state appears with an action button to "Đăng ký thiết bị đầu tiên".
5. **Given** a loading network state, **When** data is fetching, **Then** accessible skeleton rows are displayed.

---

### User Story 2 - Device Registration & One-Time Certificate Download (Priority: P2)

As a developer setting up a local machine or DevOps engineer deploying a server, I want to register my device through a modal dialog and immediately download the private mTLS certificate files (`client.crt` and `client.key`), so that my machine can cryptographically authenticate with the Zero-Trust API gateway.

**Why this priority**: Fulfills the hardware credential issuance requirement, enabling cryptographic machine identity without storing private keys permanently on the central database.

**Independent Test**: On `/clients`, click "Đăng ký thiết bị mới" -> Enter device name "MacBook Pro M3", choose "Developer PC", select "90 ngày", submit -> Receive success dialog with download buttons for `client.crt` and `client.key` -> Download both files -> Verify client appears in the directory table.

**Acceptance Scenarios**:
1. **Given** the `/clients` page, **When** clicking "Đăng ký thiết bị mới", **Then** the `RegisterClientDialog` opens with fields for Device Name (required, min 2 chars), Client Type (`USER_DEVICE` or `APP_SERVER`), and Validity Period (30, 90, 365 days).
2. **Given** valid form inputs, **When** the user clicks "Khởi tạo chứng chỉ", **Then** the system sends `POST /api/v1/gateway/clients`, shows a pending loading state, and receives the X.509 certificate and private key.
3. **Given** registration success, **When** the response arrives, **Then** the modal transitions to the `CertDownloadDialog` view displaying:
   - Certificate serial and SHA-256 fingerprint badge.
   - Prominent security alert: *"Khóa riêng (Private Key) chỉ được tạo và hiển thị 1 lần duy nhất. Hãy tải về và lưu vào thư mục ~/.dut-vault/ an toàn."*
   - Direct download buttons: "Tải client.crt" and "Tải client.key".
   - One-click "Tải cả hai tệp (ZIP/Bundle)".
4. **Given** the user closing the download dialog, **When** closed, **Then** the private key is wiped from memory, the clients list cache is refreshed, and a success toast appears.

---

### User Story 3 - Project Virtual Keys Management & Instant Revocation (Priority: P3)

As a team lead or security lead managing an application workspace, I want to issue Virtual Access Keys bound to specific registered devices on `/projects/[id]` and be able to revoke them immediately if compromised, so that stolen API keys cannot be replayed from unauthorized machines.

**Why this priority**: Enforces Constitution Principle VIII (Identity Binding 1:1 between Virtual Keys and mTLS hardware certificates).

**Independent Test**: Navigate to `/projects/[id]` -> Open the "Virtual Keys" workspace tab -> Click "Cấp Virtual Key mới" -> Select registered device -> Submit -> Copy generated raw key `vkey_dev_...` with CLI command -> Verify key row displays status `ACTIVE` -> Click "Thu hồi khóa" (Revoke) -> Key status changes immediately to `REVOKED`.

**Acceptance Scenarios**:
1. **Given** a project workspace on `/projects/[id]`, **When** clicking the "Virtual Keys" tab, **Then** the system queries `GET /api/v1/gateway/projects/{id}/keys` and renders `VirtualKeysTable`.
2. **Given** the Virtual Keys tab, **When** clicking "Cấp Virtual Key mới", **Then** the `GenerateKeyModal` opens with a dropdown populated from registered clients (`useClientsQuery`).
3. **Given** a selected client, **When** the user submits the form, **Then** the system sends `POST /api/v1/gateway/keys`, generates the key, and displays the full unmasked key token (`vkey_dev_...`) with a copy button and sample CLI instruction:
   `dut-vault run --key=vkey_dev_... -- python main.py`
4. **Given** an active virtual key row in the table, **When** clicking "Thu hồi khóa" (Revoke), **Then** a confirmation dialog prompts the user; upon confirming, `POST /api/v1/gateway/keys/{key_id}/revoke` is sent.
5. **Given** key revocation success, **When** completed, **Then** the key status badge immediately changes from `ACTIVE` (green) to `REVOKED` (rose) with revocation timestamp and Sonner toast notification.

---

### Edge Cases

- **One-Time Key and Certificate Display**: Once the modal is closed, the private key PEM and full Virtual Key token cannot be retrieved again from the backend. The UI must clearly warn the user before closing.
- **Revoked Device Handling**: If a device's certificate is revoked or expired, the key generation modal must disallow selecting that client and show an explanatory disabled tooltip.
- **Client Disassociation**: When viewing Virtual Keys, if a bound client has been revoked, the key row indicates the compromised client status.
- **File Download MIME Types**: Downloaded files must use proper MIME types (`application/x-x509-ca-cert` for `.crt` and `application/pkcs8` or `text/plain` for `.key`) and UTF-8 encoding.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Domain 1: Client & Device Directory (`/clients`)
- **FR-001**: System MUST provide a dedicated route `/clients` accessible via the AppShell navigation.
- **FR-002**: System MUST query `GET /api/v1/gateway/clients` and render registered devices in `ClientsTable` with columns: Tên thiết bị, Loại client, Fingerprint SHA-256, Hạn chứng chỉ, Trạng thái.
- **FR-003**: System MUST provide a search input filtering clients by name or certificate fingerprint.
- **FR-004**: System MUST render skeleton loading rows and empty state illustration when zero clients exist.

#### Domain 2: Device Registration & mTLS Certificate Issuance
- **FR-005**: System MUST provide `RegisterClientDialog` with inputs for Device Name, Client Type (`USER_DEVICE` / `APP_SERVER`), and Validity Period (30, 90, 365 days).
- **FR-006**: System MUST validate device registration form with Zod client-side validation.
- **FR-007**: System MUST call `POST /api/v1/gateway/clients` and handle loading states during cryptographic key pair generation.
- **FR-008**: System MUST display `CertDownloadDialog` showing certificate serial, fingerprint, and file download triggers for `client.crt` and `client.key`.
- **FR-009**: System MUST automatically trigger client-side Blob file downloads with correct filenames when download buttons are clicked.

#### Domain 3: Virtual Keys & Zero-Trust Gatekeeper
- **FR-010**: System MUST query `GET /api/v1/gateway/projects/{project_id}/keys` and render project virtual keys in `VirtualKeysTable`.
- **FR-011**: System MUST provide `GenerateKeyModal` allowing users to select any active registered client and call `POST /api/v1/gateway/keys`.
- **FR-012**: System MUST display the generated raw Virtual Key token (`vkey_dev_...`) along with copy action and CLI usage instructions.
- **FR-013**: System MUST provide a revocation action calling `POST /api/v1/gateway/keys/{key_id}/revoke` with a confirmation dialog.
- **FR-014**: System MUST update virtual key status immediately in the UI with Sonner toast feedback.

---

### Key Entities

- **Client**: Registered machine or workload identity. Attributes: `id: str`, `name: str`, `client_type: "USER_DEVICE" | "APP_SERVER"`, `owner_id: str`, `cert_fingerprint: str`, `cert_serial: str`, `expires_at: str`, `is_revoked: bool`, `created_at: str`.
- **VirtualKey**: Access token bound 1:1 to a client and project. Attributes: `id: str`, `client_id: str`, `project_id: str`, `key_prefix: str`, `status: "ACTIVE" | "REVOKED"`, `created_at: str`, `revoked_at: str | null`.
- **CertBundle**: Cryptographic pair returned upon registration. Attributes: `cert_pem: str`, `key_pem: str`, `cert_fingerprint: str`, `cert_serial: str`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Device registration and certificate file download completes in under **10 seconds**.
- **SC-002**: Generating and binding a Virtual Key to a device completes in under **5 seconds**.
- **SC-003**: Revoking a virtual key updates the status badge to `REVOKED` in under **500ms**.
- **SC-004**: Downloaded `.crt` and `.key` files are cryptographically valid X.509 PEM formatted files.
- **SC-005**: 100% type safety: passes `pnpm --prefix web typecheck` and `pnpm --prefix web build` with zero errors.
