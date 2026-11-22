# Feature Specification: Web Phase 2 - Dynamic Vault Management & Key-Level ACL

**Feature Branch**: `008-web-vault-acl`  
**Created**: 2026-11-23  
**Status**: Ready for Planning  
**Input**: Phase 2 requirements from `docs/WEB_ROADMAP.md` ("Giai Đoạn 2: Quản Lý Dynamic Vault & Phân Quyền Từng Key (Vault & ACL) - Xóa bỏ file .env thủ công. Xây dựng bảng quản lý secret phân nhóm theo Scope và modal phân quyền ai được đọc key gì").

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Scope Tabs & Encrypted Secret Management Table (Priority: P1) 🎯 MVP

As a developer or DevOps engineer managing a project workspace, I want an encrypted Key-Value configuration table grouped by Scope tabs, so that I can securely view, search, and copy environment configurations without storing plaintext `.env` files on disk.

**Why this priority**: Core deliverable of the Dynamic Vault UI. Without this table, developers cannot inspect or use the vault secrets stored in the backend.

**Independent Test**: Navigate to `/projects/[id]` -> Open the "Biến môi trường (Vault)" tab -> Verify scope tabs (e.g., "Tất cả", "Common", "Database", "Payment") are displayed -> See secrets table with masked values (`••••••••••••`) -> Click the "Eye" icon to unmask a secret value -> Click the "Copy" icon to copy the value to clipboard with a success toast.

**Acceptance Scenarios**:
1. **Given** a project workspace with existing secrets, **When** the user opens the "Biến môi trường (Vault)" tab, **Then** the system queries `GET /api/v1/vault/projects/{id}/scopes` and `GET /api/v1/vault/projects/{id}/secrets` and renders scope tabs and the `SecretsTable`.
2. **Given** secrets displayed in the table, **When** the page renders, **Then** each secret value is masked by default with bullets (`••••••••••••`) and monospace font styling (`font-mono`).
3. **Given** a masked secret value, **When** the user clicks the "Eye" toggle button, **Then** the plain value is revealed, and clicking again re-masks it.
4. **Given** a secret row, **When** the user clicks the "Copy" button, **Then** the plain value is copied to the system clipboard, and Sonner displays "Đã sao chép giá trị vào clipboard!".
5. **Given** a search query typed in the search filter bar, **When** the user enters keywords, **Then** the secrets table filters rows in real time matching the secret key or scope name.
6. **Given** a project or scope with zero secrets, **When** viewing the tab, **Then** an informative empty state is shown with a "Thêm biến mới" button.

---

### User Story 2 - Interactive Secret Creation & Edit Dialog (Priority: P2)

As a developer or system administrator, I want to add new environment secrets or update existing secrets through an accessible dialog with scope selection and validation, so that changes are immediately encrypted with AES-256-GCM and stored in the backend Vault.

**Why this priority**: Enables self-service configuration management directly from the web interface without raw curl commands or database intervention.

**Independent Test**: Click "Thêm biến mới", select or input a Scope (e.g. `Database`), enter Key (e.g. `DB_PASSWORD`) and Value, submit form -> Modal closes, success toast appears, and the new secret row immediately appears under the selected Scope tab.

**Acceptance Scenarios**:
1. **Given** the Vault workspace, **When** clicking "Thêm biến mới", **Then** a modal dialog (`SecretDialog`) opens with inputs for Scope Name (combobox / input), Secret Key (uppercase alphanumeric and underscores, min 2 chars), and Secret Value (textarea/input with hide/show toggle).
2. **Given** an invalid secret key (e.g. lowercase letters, spaces, or empty), **When** submitted, **Then** Zod client-side validation displays an inline error message and blocks submission.
3. **Given** valid inputs, **When** the user clicks "Lưu biến môi trường", **Then** the dialog sends `POST /api/v1/vault/projects/{id}/secrets` with `x-actor-id: current_user.email`, closes the dialog on 201 response, shows a success toast, and refreshes the secret list cache.
4. **Given** an existing secret in the table, **When** clicking "Sửa" (Edit), **Then** the modal pre-fills with the secret's Scope, Key, and current decrypted Value, allowing safe updates.

---

### User Story 3 - Granular Key-Level Access Control Matrix Modal (Priority: P3)

As a project administrator or security lead, I want to grant or revoke read permissions for individual secret keys to specific users or clients from the central directory, so that team members and services only have access to the exact credentials they need.

**Why this priority**: Enforces the Zero-Trust least-privilege principle (Constitution Principle VI) where access is granular per key rather than broad all-or-nothing access.

**Independent Test**: Click "Phân quyền truy cập" -> Select a user from the central DUT-AI directory dropdown -> View the list of all project secret keys with checkboxes -> Toggle checkbox for `DB_HOST` (Grant) -> Toggle checkbox for `STRIPE_KEY` (Revoke) -> Verify permissions update immediately via `POST` and `DELETE /api/v1/vault/projects/{id}/permissions`.

**Acceptance Scenarios**:
1. **Given** the Vault tab, **When** clicking the "Phân quyền truy cập" button, **Then** the `KeyPermissionMatrixModal` opens.
2. **Given** the modal open, **When** loading the user dropdown, **Then** the system queries `GET /api/v1/users/options` and lists all active directory users with their avatar, name, and email.
3. **Given** a selected user, **When** selection changes, **Then** the modal queries `GET /api/v1/vault/projects/{id}/permissions?identity_id={user_id}` and renders a checklist of all existing project secret keys with checked states corresponding to permitted keys.
4. **Given** an unchecked secret key, **When** the user checks it, **Then** the system calls `POST /api/v1/vault/projects/{id}/permissions` with `{ identity_id, identity_type: "user", secret_key }` and updates the cache.
5. **Given** a checked secret key, **When** the user unchecks it, **Then** the system calls `DELETE /api/v1/vault/projects/{id}/permissions?identity_id={identity_id}&secret_key={secret_key}` and updates the cache.
6. **Given** a network failure or permission denial, **When** toggling, **Then** the UI rolls back the checkbox and displays an error toast.

---

### Edge Cases

- **Non-Authorized Key Visibility**: If the logged-in user lacks permission for certain keys, `GET /api/v1/vault/projects/{id}/secrets` only returns the keys they are permitted to read. The UI displays what is returned and does not crash on missing keys.
- **Empty Scope or New Scope**: If the user inputs a new scope name in `SecretDialog`, the backend dynamically creates the scope and attaches the secret to it.
- **Special Characters in Secret Values**: Values containing line breaks, quotes, base64 data, or JSON strings must be preserved exactly without escaping corruption.
- **Rapid Eye Toggle & Clipboard Clearing**: Toggling eye buttons quickly must not trigger duplicate unmask operations or memory leaks.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Domain 1: Secret Exploration & Scope Navigation
- **FR-001**: System MUST query `GET /api/v1/vault/projects/{id}/scopes` and render scope tabs ("Tất cả", "Common", "Database", etc.) with active indicators.
- **FR-002**: System MUST query `GET /api/v1/vault/projects/{id}/secrets` and group or filter decrypted secrets by selected scope.
- **FR-003**: System MUST display secrets in a responsive data table (`Table`) with columns: Key, Giá trị (Value), Nhóm (Scope), and Thao tác (Actions).
- **FR-004**: System MUST mask secret values by default (`••••••••••••`) and provide a toggle button to unmask/re-mask individual secret values.
- **FR-005**: System MUST provide a one-click copy button for secret values with clipboard integration and Sonner toast notifications.
- **FR-006**: System MUST provide a search filter input to quickly find secrets by key name or scope name.
- **FR-007**: System MUST render loading skeleton rows when fetching secrets and scopes.

#### Domain 2: Secret Creation & Modification
- **FR-008**: System MUST provide a modal dialog (`SecretDialog`) for creating and editing secrets.
- **FR-009**: System MUST validate secret keys to match upper snake_case pattern (`^[A-Z0-9_]+$`, min 2 chars) via Zod.
- **FR-010**: System MUST allow selecting an existing scope or typing a new custom scope name.
- **FR-011**: On submit, system MUST send `POST /api/v1/vault/projects/{id}/secrets` with payload `{ scope_name, key, value }` and `x-actor-id` header.
- **FR-012**: System MUST invalidate TanStack Query cache keys for scopes and secrets upon successful creation/update.

#### Domain 3: Granular Key Permissions & User Directory
- **FR-013**: System MUST query `GET /api/v1/users/options` to populate the user selection dropdown in the ACL modal.
- **FR-014**: System MUST query `GET /api/v1/vault/projects/{id}/permissions?identity_id={user_id}` when an identity is selected.
- **FR-015**: System MUST render an accessible checklist/matrix displaying all secret keys available in the project with current permission state.
- **FR-016**: System MUST send `POST /api/v1/vault/projects/{id}/permissions` when granting access to a key.
- **FR-017**: System MUST send `DELETE /api/v1/vault/projects/{id}/permissions?identity_id={identity_id}&secret_key={secret_key}` when revoking access to a key.
- **FR-018**: System MUST handle permission update errors with optimistic rollback and clear toast feedback.

---

### Key Entities

- **Scope**: Configuration group (e.g., `Common`, `Database`). Attributes: `id: str`, `project_id: str`, `name: str`, `description: str | null`, `created_at: str`.
- **Secret**: Configuration key-value pair. Attributes: `key: str`, `value: str`, `scope_name: str`.
- **KeyPermission**: Granular association between an identity and a secret key. Attributes: `identity_id: str`, `identity_type: str`, `secret_key: str`, `granted_by: str`.
- **UserOption**: Central organization user. Attributes: `id: number`, `name: str`, `email: str`, `avatar_url: str | null`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Secret table loads and displays masked configurations within 1.0 second on standard connections.
- **SC-002**: Toggling mask/unmask and copy-to-clipboard actions respond in under 50ms with zero layout shifts.
- **SC-003**: Creating or updating a secret completes in under 15 seconds from opening the dialog to viewing the updated row.
- **SC-004**: Toggling key permissions reflects immediately in the UI and synchronizes with the backend in under 500ms.
- **SC-005**: 100% type safety: zero TypeScript compilation errors (`pnpm --prefix web typecheck`), zero ESLint errors, and full build pass (`pnpm --prefix web build`).
