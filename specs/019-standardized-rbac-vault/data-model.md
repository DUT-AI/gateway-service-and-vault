# Data Model: Standardized 3-Tier RBAC & Project Membership

**Feature**: `019-standardized-rbac-vault` | **Date**: 2026-11-25

## 1. New Database Table: `project_members`

Located in `modules/gateway/models/member.py`.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `String(26)` | Primary Key (ULID) | Unique membership record ID |
| `project_id` | `String(26)` | Foreign Key (`projects.id`, `ON DELETE CASCADE`), Not Null | Target project |
| `user_id` | `Integer` | Not Null, Indexed | Native integer SSO User ID from DUT-AI Manage |
| `added_by` | `Integer` | Not Null | Native integer SSO User ID of Admin who added the member |
| `created_at` | `DateTime(timezone=True)` | Server default `now()` | Record creation timestamp |
| `updated_at` | `DateTime(timezone=True)` | Server default `now()`, onupdate | Record update timestamp |

### Constraints & Indexes
- `UniqueConstraint("project_id", "user_id", name="uq_project_member_user")`: A user can only be added once per project.
- `Index("ix_project_members_user_id", "user_id")`: Optimizes `GET /projects` filtering for non-admin users.

---

## 2. Domain Entities

### `RoleTier` (Enum in `core/security/roles.py`)
```python
class RoleTier(str, Enum):
    ADMIN = "ADMIN"
    PROJECT_DEVELOPER = "PROJECT_DEVELOPER"
    OTHER = "OTHER"
```

### `UserContext` (Dataclass in `core/security/roles.py`)
- `user_id: int`
- `email: str`
- `name: str | None`
- `role_tier: RoleTier`
- `role_names: list[str]`
- `permissions: list[str]`

### `ProjectMemberEntity` (Pure Dataclass in `modules/gateway/domain/entities.py`)
- `id: str`
- `project_id: str`
- `user_id: int`
- `added_by: int`
- `created_at: datetime`
- `updated_at: datetime`

---

## 3. Existing Entities Interaction

- **`ProjectModel`** (`projects`): Has one-to-many relationship with `ProjectMemberModel` (`cascade="all, delete-orphan"`).
- **`KeyPermissionModel`** (`key_permissions`): Continues to store `identity_id: str` (e.g. `str(user_id)` or machine `client_id`) and `secret_key: str` for granular key-level ACL for `OTHER` roles and machine clients.
- **`SecretItemModel`** (`secrets`): `created_by` stores `str(user_id)` or email so creators can always be identified; `CreateSecretUseCase` grants `key_permissions` for `str(user_id)` when a non-admin creates a secret.
