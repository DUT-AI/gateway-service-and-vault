from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized response wrapper for paginated collections."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
