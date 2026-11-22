# Data Model: SSO-Only & External User Directory

**Feature Branch**: `006-sso-auth-external-users`  
**Date**: 2026-11-23  

---

## 1. Domain Entities (`modules/identity/domain/entities.py`)

Pure dataclasses without external framework dependencies (Clean Architecture Purity Gate).

### A. ExternalUserOptionEntity
Summary representation of an organization member for UI select/options dropdowns.

```python
@dataclass
class ExternalUserOptionEntity:
    id: int  # Strict integer identifier
    name: str
    email: str
    avatar_url: str | None = None
```

### B. ExternalUserDetailEntity
Complete user profile retrieved from central DUT-AI directory.

```python
@dataclass
class ExternalUserDetailEntity:
    id: int  # Strict integer identifier
    name: str
    email: str
    status: str
    phone_number: str | None = None
    role_ids: list[int] = field(default_factory=list)
    role_names: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    avatar_url: str | None = None
    discord_id: str | None = None
    zalo_bot_id: str | None = None
    check_in_card_code_configured: bool = False
```

### C. SsoSessionEntity
Active authenticated caller identity.

```python
@dataclass
class SsoSessionEntity:
    user_id: int  # Strict integer identifier
    email: str
    name: str | None = None
    role_names: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    avatar_url: str | None = None
```

---

## 2. Pydantic DTOs (`modules/identity/dtos/user_dtos.py`)

Pydantic v2 models representing external payloads and HTTP responses.

```python
from pydantic import BaseModel, Field


class UserOptionResponse(BaseModel):
    id: int = Field(..., description="Unique user integer identifier")
    name: str
    email: str
    avatar_url: str | None = None


class UserDetailResponse(BaseModel):
    id: int = Field(..., description="Unique user integer identifier")
    name: str
    email: str
    phone_number: str | None = None
    status: str
    role_ids: list[int] = Field(default_factory=list)
    role_names: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    avatar_url: str | None = None
    discord_id: str | None = None
    zalo_bot_id: str | None = None
    check_in_card_code_configured: bool = False
```

---

## 3. Database Impact Analysis

- **Local `users` table**: No longer used for password authentication or local registration.
- **Foreign Keys**: No existing foreign key constraints in `projects`, `clients`, `key_permissions`, or `secrets` reference `users.id`.
- **Database Schema**: Zero local credentials stored. Clean separation of concerns.
