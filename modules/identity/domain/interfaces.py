from typing import Protocol

from modules.identity.domain.entities import (
    ExternalUserDetailEntity,
    ExternalUserOptionEntity,
)


class IExternalUserDirectoryService(Protocol):
    """Protocol for remote DUT-AI user directory queries."""

    async def get_user_options(
        self, auth_token: str | None = None
    ) -> list[ExternalUserOptionEntity]:
        """Fetch all user options from central directory (with caching)."""
        ...

    async def get_user_by_id(
        self, user_id: int, auth_token: str | None = None
    ) -> ExternalUserDetailEntity | None:
        """Fetch full user details by integer ID from central directory (with caching)."""
        ...

    async def invalidate_cache(self, user_id: int | None = None) -> None:
        """Invalidate user cache in Redis."""
        ...
