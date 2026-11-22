from dataclasses import dataclass, field
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


@dataclass
class ExternalUserOptionEntity:
    """Summary representation of a user from the central directory."""

    id: int  # Strict integer identifier
    name: str
    email: str
    avatar_url: str | None = None


@dataclass
class ExternalUserDetailEntity:
    """Complete user profile from the central directory."""

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


@dataclass
class SsoSessionEntity:
    """Active authenticated SSO session."""

    user_id: int  # Strict integer identifier
    email: str
    name: str | None = None
    role: str = "user"
    role_names: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    avatar_url: str | None = None


__all__ = [
    "AuthPayload",
    "ExternalUserDetailEntity",
    "ExternalUserOptionEntity",
    "SsoSessionEntity",
    "UserEntity",
]
