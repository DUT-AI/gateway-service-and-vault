# Quickstart & Validation Guide: Standardized 3-Tier RBAC

**Feature**: `019-standardized-rbac-vault` | **Date**: 2026-11-25

## Prerequisites

- PostgreSQL & Redis running (`docker compose up -d postgres redis`)
- Database migrations applied: `uv run alembic upgrade head`

## Validation Scenarios

### 1. Run Automated RBAC Integration & Purity Tests
```bash
uv run pytest tests/integration/test_rbac_3_tier.py tests/integration/test_vault_rbac.py tests/test_clean_architecture_purity.py
```

### 2. Verify Type Safety & Linting
```bash
uv run ruff check .
make check
```

### 3. Manual E2E Walkthrough
1. **Admin**: Log in as `admin`, create Project A and Project B. Add `Project Developer` (User 2) and `Trainer` (User 3) to Project A only. Create secrets `DB_URL` and `STRIPE_KEY` in Project A.
2. **Project Developer (User 2)**: Log in and verify only Project A is visible (Project B returns 403). Open Project A Vault -> verify both `DB_URL` and `STRIPE_KEY` are readable. Verify "Tạo dự án mới" and "Quản lý thành viên" are hidden/forbidden.
3. **Trainer (User 3)**: Log in and verify only Project A is visible. Open Project A Vault -> verify `DB_URL` and `STRIPE_KEY` are hidden. Create `TRAINER_NOTE` -> verify `TRAINER_NOTE` appears immediately for User 3, while `DB_URL` remains hidden until Admin grants permission.
