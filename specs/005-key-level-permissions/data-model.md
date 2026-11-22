# Phase 1: Data Model - Granular Key-Level Secret Permissions

**Feature**: `005-key-level-permissions`  
**Date**: 2026-11-23  
**Status**: Completed  

---

## 1. Domain Entities (`modules/vault/domain/entities.py`)

Pure Python dataclasses (Zero framework imports per Constitution Principle I).

### `KeyPermissionEntity`
Represents an explicit authorization grant allowing a specific identity to read a specific secret key.

```python
@dataclass
class KeyPermissionEntity:
    id: str
    project_id: str
    identity_id: str
    secret_key: str
    identity_type: str = "client"  # "client" or "user"
    granted_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_wildcard(self) -> bool:
        return self.secret_key == "*"
```

**Validation & Invariants**:
- `project_id`: Non-empty string (26-character ULID).
- `identity_id`: Non-empty string (up to 100 characters).
- `secret_key`: Non-empty string (up to 100 characters); alphanumeric with underscores/dashes, or `*`.
- `identity_type`: Must be `"client"` or `"user"`.

---

## 2. Infrastructure Models (`modules/vault/models/permission.py`)

SQLAlchemy 2.0 declarative model.

```python
class KeyPermissionModel(Base, ULIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for granular identity-to-key secret permissions."""

    __tablename__ = "key_permissions"

    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    identity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    identity_type: Mapped[str] = mapped_column(String(20), default="client", nullable=False)
    secret_key: Mapped[str] = mapped_column(String(100), nullable=False)
    granted_by: Mapped[str] = mapped_column(String(100), default="", nullable=False)

    __table_args__ = (
        UniqueConstraint("project_id", "identity_id", "secret_key", name="uq_project_identity_key"),
        Index("ix_key_permissions_lookup", "project_id", "identity_id"),
    )
```

---

## 3. Application & API DTOs (`modules/vault/dtos/vault_dtos.py`)

Pydantic v2 schemas for request validation and response serialization.

### `GrantKeyPermissionRequest`
```python
class GrantKeyPermissionRequest(BaseModel):
    identity_id: str = Field(..., min_length=1, max_length=100)
    identity_type: str = Field(default="client", pattern="^(client|user)$")
    secret_key: str = Field(..., min_length=1, max_length=100)
```

### `RevokeKeyPermissionRequest`
```python
class RevokeKeyPermissionRequest(BaseModel):
    identity_id: str = Field(..., min_length=1, max_length=100)
    secret_key: str = Field(..., min_length=1, max_length=100)
```

### `KeyPermissionResponse`
```python
class KeyPermissionResponse(BaseModel):
    id: str
    project_id: str
    identity_id: str
    identity_type: str
    secret_key: str
    granted_by: str
    created_at: datetime
```

### `IdentityPermissionsResponse`
```python
class IdentityPermissionsResponse(BaseModel):
    project_id: str
    identity_id: str
    permitted_keys: list[str]
```
