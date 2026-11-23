# Quickstart Validation Guide: Project Upstream Service Binding & Quota Governance

**Feature Branch**: `012-project-service-binding`
**Created**: 2026-11-23

## Overview

This guide details end-to-end verification steps for Project Upstream Service Binding & Quota Governance across the backend test suite, API synchronization, and the Next.js frontend UI.

---

## 1. Automated Backend Unit & Integration Tests

Run the test suite verifying domain purity, service binding use cases, and repository persistence:

```bash
uv run pytest tests/test_project_service_binding.py -v
```

Expected output:
- `test_bind_service_to_project_success` PASSED
- `test_bind_duplicate_service_raises_conflict` PASSED
- `test_unbind_service_from_project_success` PASSED
- `test_update_service_quota_policy_success` PASSED
- `test_gateway_verification_blocks_unauthorized_service` PASSED

---

## 2. API Contract & TypeScript Types Synchronization

Verify that backend FastAPI schemas synchronize cleanly to the web application:

```bash
make api-types
```

Expected output:
- OpenAPI schema generated at `openapi.json`
- TypeScript definitions synchronized in `web/src/types/api.ts`

---

## 3. Frontend Type Checking & Production Build

Verify strict TypeScript compilation and production bundle build:

```bash
pnpm --prefix web typecheck
pnpm --prefix web build
```

Expected output:
- Zero type errors (`Found 0 errors`).
- Next.js build succeeds with static optimization for all workspace routes (`/projects/[id]`, `/services`, etc.).

---

## 4. Manual End-to-End Verification Flow

1. **Navigate to Project Workspace**:
   - Open browser at `http://localhost:3000/projects`.
   - Click on an existing project (e.g. `Payment Gateway Sandbox`).
2. **Access "Dịch vụ liên kết" Tab**:
   - Click on the new tab `"Dịch vụ liên kết"`.
   - Verify empty state appears if no services are bound yet.
3. **Bind an Upstream Service**:
   - Click `"Thêm dịch vụ"` (Add Service).
   - In the modal dialog, select an available upstream service (e.g. `OpenAI API`).
   - Enter `120` for Rate Limit (RPM) and `50000` for Daily Quota.
   - Click `"Xác nhận liên kết"`.
   - Observe toast notification and service appearing in table with active status badges.
4. **Test Duplicate Prevention**:
   - Click `"Thêm dịch vụ"` again.
   - Verify that `OpenAI API` is either excluded or disabled in the service dropdown.
5. **Revoke Service Access**:
   - In the table row for `OpenAI API`, click `"Xóa quyền"` (Revoke).
   - Confirm the prompt in the alert dialog.
   - Verify that `OpenAI API` is immediately removed from the table.
