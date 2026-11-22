# Quickstart & Validation Guide: Web Phase 1 - Project Hub & Core Navigation

**Feature**: `007-web-project-hub`  
**Date**: 2026-11-23  

This guide provides end-to-end verification steps to validate Phase 1 functionality in browser and via automated checks.

## Prerequisites

1. PostgreSQL, Redis, and backend API running:
   ```bash
   uv run fastapi dev apps/api/main.py
   # Or verify via curl:
   curl -s http://localhost:8000/health
   ```
2. Frontend dependencies installed:
   ```bash
   cd web && pnpm install
   ```

---

## 1. Automated Verification Gates

Run static analysis and compilation checks:
```bash
# 1. Frontend Typecheck
pnpm --prefix web typecheck

# 2. Frontend Production Build
pnpm --prefix web build

# 3. Backend Verification
uv run pytest tests/integration/test_gateway_management_api.py
```

Expected Outcome: All 3 commands exit with code 0 without any warnings or type errors.

---

## 2. Interactive Browser Scenarios

Start frontend dev server:
```bash
pnpm --prefix web dev
```
Open `http://localhost:3000` in Google Chrome or testing browser.

### Scenario A: Navigation & User Identity Display (US1)
1. Log in with DUT-AI SSO credentials at `http://localhost:3000/login`.
2. Observe redirection to `/dashboard` or `/projects`.
3. Verify AppShell sidebar shows:
   - "DUT AI Platform - Secure Gateway & Dynamic Vault" header.
   - Navigation links: "Dashboard", "Dự án (Projects)", "Thiết bị mTLS (Clients)", "Dịch vụ (Services)".
   - Current user avatar, full name, email, and "Đã xác thực DUT" shield badge.
4. Verify project list renders at `/projects`:
   - If empty: Displays friendly empty state illustration with "Tạo dự án đầu tiên" button.
   - If projects exist: Displays responsive card grid with title, slug, description, and creation date.

### Scenario B: Project Creation Modal (US2)
1. On `/projects`, click the **"Tạo dự án mới"** button.
2. Verify modal dialog (`Dialog`) opens with focus on the Project Name input.
3. Type: `Hệ Thống Thanh Toán Core`.
4. Verify slug automatically suggests: `he-thong-thanh-toan-core`.
5. Enter description: `Quản lý cổng thanh toán trực tuyến`.
6. Click **"Tạo dự án"**.
7. Verify:
   - Submit button enters loading state.
   - Dialog closes upon success.
   - Sonner toast appears: *"Tạo dự án thành công"*.
   - New project card appears in the grid immediately without refreshing the page.

### Scenario C: Project Workspace & Breadcrumb Navigation (US3)
1. Click on the newly created project card in `/projects`.
2. Verify browser navigates to `/projects/[project-id]`.
3. Verify top breadcrumb displays: `Dự án > Hệ Thống Thanh Toán Core`.
4. Verify project metadata header shows name, slug badge, description, and created timestamp.
5. Verify workspace sub-tabs:
   - "Biến môi trường (Vault)" (active tab).
   - "Virtual Keys" tab.
   - "Cài đặt" tab.
6. Click breadcrumb link "Dự án" -> smoothly navigates back to `/projects`.
