from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class UserEntity:
    """Core domain user entity representing identity."""

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


@dataclass
class AuthPayload:
    """Domain representation of authenticated user session."""

    user_id: int
    email: str | None = None
    role: str = "user"
    raw_payload: dict[str, Any] | None = None


__all__ = ["AuthPayload", "UserEntity"]
