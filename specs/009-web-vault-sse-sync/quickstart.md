# Quickstart Validation Guide: Web Phase 3 - Real-Time Vault Hot-Reload Stream (SSE Live Sync)

**Feature**: `009-web-vault-sse-sync`  
**Date**: 2026-11-23  

This guide provides steps to verify the Real-Time In-Memory Hot-Reload Stream (SSE Live Sync) end-to-end.

---

## 1. Automated Validation Gates

Verify contracts, static types, and test suites with zero errors:

```bash
# 1. Typecheck the Next.js frontend
pnpm --prefix web typecheck

# 2. Build the Next.js production bundle
pnpm --prefix web build

# 3. Verify all backend unit and integration test suites
uv run pytest
```

---

## 2. Interactive Dual-Window Live Sync Verification

### Prerequisites
1. Start Redis:
   ```bash
   redis-server
   ```
2. Start the FastAPI backend server:
   ```bash
   uv run uvicorn apps.api.main:app --reload --port 8000
   ```
3. Start the Next.js frontend development server:
   ```bash
   pnpm --prefix web dev
   ```

---

### Step-by-Step Test Procedure

1. Open **Browser Window A** at `http://localhost:3000/projects/[project_id]`.
2. Open **Browser Window B** side-by-side at the same URL.
3. Select the **"Biến môi trường (Vault)"** tab in both windows.
4. **Verify Initial Connection**:
   - Both windows display the `LiveSyncStatusBadge` with a pulsating green indicator: **"Live Sync"**.
   - Hovering over the badge displays tooltip: *"Đang kết nối luồng SSE trực tiếp"*.
5. **Trigger Live Configuration Update**:
   - In **Window A**, click **"Thêm biến mới"** (or edit an existing key).
   - Enter Scope `Common`, Key `REDIS_CACHE_TTL`, and Value `3600`.
   - Click **"Lưu biến môi trường"**.
6. **Verify Real-Time Synchronization (< 3 seconds)**:
   - In **Window B**, observe:
     1. A Sonner notification toast appears immediately: *"huynhphuocnguyen.dev@gmail.com vừa cập nhật biến REDIS_CACHE_TTL (Scope: Common)"*.
     2. The secrets table automatically refreshes without full page reload.
     3. The row for `REDIS_CACHE_TTL` glows with a brief highlight animation for 2.5 seconds.
7. **Verify Live Audit Feed**:
   - In **Window B**, click **"Nhật ký Live"** in the toolbar.
   - Inspect the event card: shows `REDIS_CACHE_TTL`, Scope `Common`, Version, Actor, and timestamp *"vừa xong"*.
8. **Verify Disconnection & Reconnection**:
   - Temporarily toggle network offline in browser DevTools or restart backend.
   - Observe badge transition to amber: **"Đang kết nối lại..."**.
   - Restore network $\rightarrow$ badge automatically returns to green: **"Live Sync"**.
