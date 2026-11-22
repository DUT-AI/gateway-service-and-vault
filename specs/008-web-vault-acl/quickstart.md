# Quickstart Validation Guide: Web Phase 2 - Dynamic Vault Management & Key-Level ACL

**Feature**: `008-web-vault-acl`  
**Date**: 2026-11-23  

This guide provides steps to verify the Dynamic Vault Management and Key-Level Access Control (ACL) features end-to-end.

---

## 1. Automated Validation Gates

Run the automated verification suite to guarantee zero contract regressions, zero TypeScript errors, and production build readiness:

```bash
# 1. Typecheck the Next.js frontend
pnpm --prefix web typecheck

# 2. Build the Next.js frontend production bundle
pnpm --prefix web build

# 3. Verify all backend unit and integration test suites
uv run pytest
```

---

## 2. Interactive Browser Verification Workflows

### Prerequisites
1. Start the backend API server:
   ```bash
   uv run uvicorn apps.api.main:app --reload --port 8000
   ```
2. Start the frontend Next.js development server:
   ```bash
   pnpm --prefix web dev
   ```
3. Open `http://localhost:3000` and ensure you are logged in via DUT-AI SSO.

---

### Scenario A: Scope Tabs & Secret Value Masking/Copy (User Story 1 - P1)

1. Navigate to `/projects`.
2. Click on any project card (or create one named "Test Vault App") to enter `/projects/[id]`.
3. In the sub-tabs, select **"Biến môi trường (Vault)"**.
4. **Verify**:
   - Scope tabs ("Tất cả", "Common", "Database", etc.) are displayed at the top.
   - Secret table lists columns: **Key**, **Giá trị**, **Nhóm (Scope)**, **Thao tác**.
   - Secret values are masked by default (`••••••••••••`).
5. Click the **Eye icon** on a row:
   - Value unmasks to plaintext (e.g. `supersecretpassword`).
   - Clicking again masks the value.
6. Click the **Copy button**:
   - Sonner toast appears: *"Đã sao chép giá trị vào clipboard!"*.
   - Paste into any text editor to verify the plaintext value matches.
7. Type in the **Search Filter** input (e.g. `DB_`):
   - Table immediately filters to display only matching keys.

---

### Scenario B: Add & Edit Encrypted Secret (User Story 2 - P2)

1. On the Vault tab, click **"Thêm biến mới"**.
2. In the `SecretDialog`:
   - Scope: Select an existing scope or type `Payment`.
   - Key: Enter `STRIPE_SECRET_KEY`.
   - Value: Enter `sk_live_948293489238492`.
3. Click **"Lưu biến môi trường"**:
   - Button shows loading state (`Đang lưu...`).
   - Modal closes automatically upon 201 response.
   - Sonner toast appears: *"Đã lưu biến môi trường thành công!"*.
   - The new secret `STRIPE_SECRET_KEY` immediately appears under the `Payment` scope tab.
4. Click **"Sửa" (Edit)** on `STRIPE_SECRET_KEY`:
   - Modal pre-fills with current scope, key, and decrypted value.
   - Modify the value to `sk_live_updated_9999` and submit.
   - Verify table updates with the new version.

---

### Scenario C: Granular Key Permissions Matrix (User Story 3 - P3)

1. In the Vault tab header, click **"Phân quyền truy cập"**.
2. In the `KeyPermissionMatrixModal`:
   - Select a team member from the **User Dropdown** (fetched from `GET /api/v1/users/options`).
   - Observe the checklist showing all secret keys in the project (`DATABASE_URL`, `STRIPE_SECRET_KEY`).
3. Check the box for `STRIPE_SECRET_KEY`:
   - Checkbox updates with a success toast (*"Đã cấp quyền đọc key STRIPE_SECRET_KEY"*).
4. Uncheck the box for `STRIPE_SECRET_KEY`:
   - Checkbox updates with a toast (*"Đã thu hồi quyền đọc key STRIPE_SECRET_KEY"*).
5. Switch to a different user in the dropdown:
   - Checkboxes update dynamically reflecting that user's specific permissions.
