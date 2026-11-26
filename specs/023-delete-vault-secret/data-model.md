# Data Model: Delete Vault Environment Variable

**Feature**: `023-delete-vault-secret`

## Entities & DTOs

### `SecretModel` / `SecretVersionModel` (existing)
- Deleting a `SecretModel` row cascades to its `SecretVersionModel` history rows (`ondelete="CASCADE"`).
- No database schema migrations required.

### `DeleteSecretResponse` (new Pydantic DTO in `modules/vault/dtos/vault_dtos.py`)
- `message: str`
- `project_id: str`
- `scope_name: str`
- `key: str`
