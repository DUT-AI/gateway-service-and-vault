# Quickstart Validation Guide: Delete Vault Environment Variable

**Feature**: `023-delete-vault-secret`

## Automated Verification
1. `make api-types && cd web && pnpm typecheck && pnpm lint`
2. `uv run ruff check --fix && uv run ruff format`
3. `uv run pytest tests/integration/test_delete_vault_secret.py tests/test_clean_architecture_purity.py`

## Manual UI Flow
1. Open a project → **Biến môi trường (Vault)** tab.
2. Click the Trash (`Xóa`) icon on any secret row.
3. Confirm deletion in `DeleteSecretDialog`.
4. Verify the row disappears immediately and scope count decrements.
