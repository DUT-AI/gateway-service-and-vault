from dataclasses import dataclass
from enum import Enum
from typing import Any


class RoleTier(str, Enum):
    """3-tier authorization classification derived from SSO role claims."""

    ADMIN = "ADMIN"
    PROJECT_DEVELOPER = "PROJECT_DEVELOPER"
    OTHER = "OTHER"


@dataclass(frozen=True)
class UserContext:
    """Resolved authenticated user context from verified SSO token."""

    user_id: int
    email: str
    name: str | None
    role_tier: RoleTier
    role_names: tuple[str, ...]
    permissions: tuple[str, ...]

    @property
    def is_admin(self) -> bool:
        return self.role_tier == RoleTier.ADMIN

    @property
    def is_developer(self) -> bool:
        return self.role_tier == RoleTier.PROJECT_DEVELOPER

    @property
    def is_other(self) -> bool:
        return self.role_tier == RoleTier.OTHER


def resolve_user_role_tier(payload: dict[str, Any]) -> RoleTier:
    """Resolve highest-precedence RoleTier from SSO token payload.

    Precedence: ADMIN > PROJECT_DEVELOPER > OTHER.
    """
    raw_roles = list(payload.get("role_names") or [])
    if payload.get("role"):
        raw_roles.append(str(payload["role"]))

    normalized_roles = {str(r).strip().lower() for r in raw_roles if r}
    permissions = {str(p).strip() for p in (payload.get("permissions") or []) if p}

    if (
        normalized_roles.intersection({"admin", "system", "superuser"})
        or "*" in permissions
    ):
        return RoleTier.ADMIN

    if (
        "project developer" in normalized_roles
        or "project_developer" in normalized_roles
    ):
        return RoleTier.PROJECT_DEVELOPER

    return RoleTier.OTHER


def build_user_context(payload: dict[str, Any]) -> UserContext:
    """Construct an immutable UserContext from a validated SSO payload dict."""
    raw_user_id = payload.get("user_id") or payload.get("sub") or 0
    user_id = int(raw_user_id)
    role_names = tuple(str(r) for r in (payload.get("role_names") or []) if r)
    permissions = tuple(str(p) for p in (payload.get("permissions") or []) if p)

    return UserContext(
        user_id=user_id,
        email=str(payload.get("email") or ""),
        name=payload.get("name"),
        role_tier=resolve_user_role_tier(payload),
        role_names=role_names,
        permissions=permissions,
    )
