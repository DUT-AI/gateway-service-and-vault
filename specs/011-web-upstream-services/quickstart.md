# Quickstart & Verification Guide: Web Phase 5 - Upstream Services & System Polish (DoD)

**Feature Branch**: `011-web-upstream-services`  
**Date**: 2026-11-23  
**Status**: Ready for Verification  

---

## 1. Prerequisites & Environment Setup

Ensure backend API and frontend development servers are active:

```bash
# Terminal 1: Backend API
cd /Users/nguyenhuynh/Documents/projects/gateway-service-and-vault
uv run fastapi dev apps/api/main.py --port 8000

# Terminal 2: Web Application
cd /Users/nguyenhuynh/Documents/projects/gateway-service-and-vault/web
pnpm dev --port 3000
```

---

## 2. Interactive End-to-End Verification Scenarios

### Scenario 1: Upstream Services Catalog & Real-Time Filtering
1. Open `http://localhost:3000/services` (or click "Dịch vụ hệ thống" in AppShell sidebar).
2. Observe page header: "Quản lý dịch vụ Upstream" with "Gateway Reverse Proxy" badge.
3. In the search box, type a service name or domain (e.g., `openai`).
4. Verify table filters rows in real time.
5. Filter by Auth Type pill (e.g. `Bearer Token`, `API Key`) -> Verify rows update accordingly.
6. Clear search input -> All registered services reappear.

---

### Scenario 2: Service Declaration & Auto-Slug Syncing
1. On `/services`, click **"Khai báo dịch vụ mới"** in the top-right toolbar.
2. In `CreateServiceDialog`:
   - **Tên dịch vụ**: Enter `Cổng Thanh Toán VNPay`
   - Observe **Slug** auto-populates with `cong-thanh-toan-vnpay`
   - **Base URL**: Enter `https://sandbox.vnpayment.vn/paymentv2`
   - **Phương thức xác thực**: Select `API Key (X-API-Key)`
   - **Thông tin xác thực (Credential)**: Enter `test_secret_key_12345`
   - Toggle the Eye icon to view/hide masked credential
   - **Thời gian chờ (Timeout)**: Select `30 giây`
3. Click **"Lưu dịch vụ upstream"**.
4. Observe:
   - Pending spinner indicates secure transmission.
   - Success toast appears: *"Khai báo dịch vụ upstream thành công!"*.
   - Dialog closes and form state is completely wiped from browser memory.
   - New service appears in the table with status badge `Đang hoạt động`.

---

### Scenario 3: Complete Cross-Module Navigation Walkthrough (DoD)
1. Navigate across all 5 modules from the sidebar:
   - **Dashboard** (`/dashboard`): Platform metrics and quick links.
   - **Dự án** (`/projects`): Project cards, Vietnamese auto-slug creation dialog.
   - **Project Detail** (`/projects/[id]`):
     - **Biến môi trường (Vault)**: Real-time SSE live sync badge, encrypted secrets table, granular key permission matrix.
     - **Virtual Keys**: Issued access keys, one-time raw secret display, CLI run snippet, and instant revocation.
     - **Cài đặt dự án**: Project metadata and system parameters.
   - **Thiết bị & Client** (`/clients`): mTLS hardware inventory, X.509 cert and private key one-time downloads.
   - **Dịch vụ hệ thống** (`/services`): Upstream partner services catalog and proxy route governance.
2. Verify active link styling (blue background/text) highlights correctly for each selected menu item.

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
