from typing import Protocol


class IUnitOfWork(Protocol):
    """Protocol for transaction boundary control."""

    async def commit(self) -> None:
        """Commit every change of the current transaction. Raises on failure."""
        ...

    async def rollback(self) -> None:
        """Discard every uncommitted change."""
        ...
