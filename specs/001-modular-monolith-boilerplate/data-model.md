# Phase 1 Data Model: Modular Monolith Boilerplate (DUT-AI Style)

## 1. Domain Entities (`modules/identity/domain/entities.py`)

All domain entities are strictly framework-independent Python dataclasses (ZERO imports from `pydantic`, `fastapi`, `sqlalchemy`).

### `UserEntity`
Core domain identity entity.

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class UserEntity:
    id: int
    email: str
    name: str | None = None
    role: str = "user"
    password_hash: str | None = None
    avatar_url: str | None = None
    status: str = "ACTIVE"
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_active(self) -> bool:
        return self.status == "ACTIVE"

    def is_admin(self) -> bool:
        return self.role == "admin"
```

### `AuthPayload`
Domain representation of a verified authentication session.

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class AuthPayload:
    user_id: int
    email: str | None = None
    role: str = "user"
    raw_payload: dict[str, Any] | None = None
```

---

## 2. ORM Persistence Models (`modules/identity/models/user.py`)

SQLAlchemy 2.0 mapped models subclassing `core.database.base.Base`.

### `UserModel`
Table: `users`

```python
from datetime import datetime
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database.base import Base

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
```

---

## 3. Data Transfer Objects (DTOs) (`modules/identity/dtos/auth_dtos.py`)

Pydantic schemas used for API contract, validation, and serialization.

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str | None = Field(None, max_length=255)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str | None = None
    role: str
    avatar_url: str | None = None
    status: str
    created_at: datetime
```

---

## 4. Shared Infrastructure Models (`core/events/models.py`)

### `OutboxEventModel`
Table: `outbox_events`

```python
from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column
from core.database.base import Base

class OutboxEventModel(Base):
    __tablename__ = "outbox_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # ULID / UUID
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
```
