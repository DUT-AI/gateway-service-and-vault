# Quickstart & Validation Guide

**Feature**: `021-dev-device-project-binding` | **Date**: 2026-11-25

## Automated Tests
```bash
uv run pytest tests/integration/test_dev_device_project_binding.py tests/integration/test_client_ownership_scoping.py tests/integration/test_rbac_3_tier.py tests/test_clean_architecture_purity.py
```

## Type Check & Lint
```bash
uv run ruff check .
cd web && pnpm typecheck
```
