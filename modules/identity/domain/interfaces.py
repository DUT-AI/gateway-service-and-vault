from typing import Protocol

from modules.identity.domain.entities import (
    ExternalUserDetailEntity,
    ExternalUserOptionEntity,
    UserEntity,
)


class IUserRepository(Protocol):
    """Protocol for User repository persistence operations."""

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        """Fetch user by primary key ID."""
        ...

    async def get_by_email(self, email: str) -> UserEntity | None:
        """Fetch user by unique email."""
        ...

    async def create(
        self,
        email: str,
        password_hash: str,
        name: str | None = None,
        role: str = "user",
    ) -> UserEntity:
        """Create and persist a new user."""
        ...

    async def update(self, user: UserEntity) -> UserEntity:
        """Update existing user state."""
        ...

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
    ) -> tuple[list[UserEntity], int, int]:
        """Fetch paginated list of users returning (items, total_count, total_pages)."""
        ...


class IExternalUserDirectoryService(Protocol):
    """Protocol for remote DUT-AI user directory queries."""

    async def get_user_options(
        self, auth_token: str | None = None
    ) -> list[ExternalUserOptionEntity]:
        """Fetch all user options from central directory."""
        ...

    async def get_user_by_id(
        self, user_id: int, auth_token: str | None = None
    ) -> ExternalUserDetailEntity | None:
        """Fetch full user details by integer ID from central directory."""
        ...
