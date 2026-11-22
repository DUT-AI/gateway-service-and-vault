from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Parameters for paginated collection queries."""

    page: int = Field(default=1, ge=1, description="Page number starting at 1")
    page_size: int = Field(
        default=20, ge=1, le=100, description="Items per page (maximum 100)"
    )
    search: str | None = Field(
        default=None, max_length=100, description="Optional search term"
    )
