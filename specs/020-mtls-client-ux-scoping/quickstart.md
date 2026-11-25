# Quickstart & Validation Guide: mTLS Client & Key UX

**Feature**: `020-mtls-client-ux-scoping` | **Date**: 2026-11-25

## Automated Tests
```bash
uv run pytest tests/integration/test_client_ownership_scoping.py tests/test_clean_architecture_purity.py
```

## Type Check & Lint
```bash
uv run ruff check .
cd web && pnpm typecheck
```
