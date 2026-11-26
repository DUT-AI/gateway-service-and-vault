# API Contract: Delete Vault Environment Variable

**Feature**: `023-delete-vault-secret`

## `DELETE /api/v1/vault/projects/{project_id}/secrets`

### Query Parameters
- `scope_name: str` (required, min_length=1)
- `key: str` (required, min_length=1)

### Authorization
- Requires authenticated user context (`get_current_user_context`) + `ensure_project_access(project_id, user_ctx, membership_uc)`.
- `ADMIN`: allowed across all projects.
- `PROJECT_DEVELOPER`: allowed in assigned projects.
- `OTHER`: allowed in assigned projects only if `key` is in `key_permissions` for `str(user_ctx.user_id)`; otherwise `403 Forbidden`.

### Responses
- `200 OK`: `DeleteSecretResponse`
  ```json
  {
    "message": "Secret deleted successfully",
    "project_id": "01M89S04YQHQ34B4HT35Y9RFTY",
    "scope_name": "Common",
    "key": "TEMP_KEY"
  }
  ```
- `403 Forbidden`: User is not a project member or `RoleTier.OTHER` lacks key permission.
- `404 Not Found`: Secret `(project_id, scope_name, key)` does not exist.
