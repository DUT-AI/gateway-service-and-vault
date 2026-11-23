# Quickstart & Verification Guide: Web Phase 4 - mTLS Device Management & Virtual Keys

**Feature Branch**: `010-web-mtls-virtual-keys`  
**Date**: 2026-11-23  
**Status**: Ready for Verification  

---

## 1. Prerequisites & Environment Setup

Ensure backend API and frontend development server are running:

```bash
# Terminal 1: Backend API (FastAPI)
cd /Users/nguyenhuynh/Documents/projects/gateway-service-and-vault
uv run fastapi dev apps/api/main.py --port 8000

# Terminal 2: Web App (Next.js)
cd /Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/web
pnpm dev --port 3000
```

---

## 2. Interactive End-to-End Verification Scenarios

### Scenario 1: Register Device & Download mTLS Certificates
1. Open `http://localhost:3000/clients` (or click "Thiết bị & Client" in AppShell sidebar).
2. Click **"Đăng ký thiết bị mới"** button in the top right.
3. In the registration dialog:
   - **Tên thiết bị**: Enter `MacBook M3 Dev`
   - **Loại thiết bị**: Select `Developer PC (USER_DEVICE)`
   - **Thời hạn chứng chỉ**: Select `90 ngày`
   - Click **"Khởi tạo chứng chỉ mTLS"**.
4. Observe transition to `CertDownloadDialog`:
   - Verify SHA-256 fingerprint badge is displayed.
   - Click **"Tải client.crt"** -> Browser downloads `client.crt` containing valid PEM.
   - Click **"Tải client.key"** -> Browser downloads `client.key` containing private key PEM.
5. Close the dialog.
6. Verify `MacBook M3 Dev` appears as an active row in the clients table.

---

### Scenario 2: Search & Filter Client Devices
1. In the search box on `/clients`, type `MacBook`.
2. Verify table filters to matching rows.
3. Type non-existent name `xyz123` -> Verify empty state message: *"Không tìm thấy thiết bị phù hợp"*.
4. Clear search bar -> All devices return.

---

### Scenario 3: Issue Virtual Access Key Bound to Device
1. Navigate to `/projects` and select any existing project (e.g., `/projects/<project-id>`).
2. Click the **"Virtual Keys"** tab in `ProjectWorkspaceTabs`.
3. Click **"Cấp Virtual Key mới"**.
4. In `GenerateKeyModal`:
   - Select `MacBook M3 Dev` from the registered client dropdown.
   - Click **"Tạo Virtual Key"**.
5. Observe the one-time display step:
   - Verify the full raw key `vkey_dev_...` is shown in a secure amber banner.
   - Click the Copy icon next to the key -> Verify checkmark feedback and toast notification.
   - Verify the CLI usage command displays:
     ```bash
     dut-vault run --key=vkey_dev_... -- python main.py
     ```
   - Click "Sao chép lệnh CLI" -> Command copied to clipboard.
6. Click "Đã lưu an toàn & Hoàn tất".
7. Verify the new key row appears in the Virtual Keys table with status badge `ACTIVE` (emerald) and prefix `vkey_dev_...`.

---

### Scenario 4: Instant Virtual Key Revocation
1. In the Virtual Keys table, locate an `ACTIVE` key row.
2. Click the **"Thu hồi"** (Revoke) button with the red shield icon.
3. A confirmation dialog appears: *"Bạn có chắc chắn muốn thu hồi Virtual Key này không? Thao tác này sẽ ngắt kết nối ngay lập tức tại Gateway và không thể hoàn tác."*
4. Click **"Xác nhận thu hồi"**.
5. Observe:
   - Success toast appears: *"Đã thu hồi Virtual Key thành công"*.
   - Key status badge immediately switches to `REVOKED` (rose color).
   - "Thu hồi" button is disabled or hidden for that row.

---

## 3. Automated Type & Build Validation Commands

Run from the repository root:

```bash
# 1. Type check Next.js application
pnpm --prefix web typecheck

# 2. Production build verification
pnpm --prefix web build

# 3. Backend unit and integration tests (Clean architecture & Gateway models)
uv run pytest
```
