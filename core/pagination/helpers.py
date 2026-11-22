import math
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from core.pagination.params import PaginationParams


async def paginate_query(
    session: AsyncSession,
    stmt: Select[Any],
    params: PaginationParams,
) -> tuple[list[Any], int, int]:
    """Execute a paginated query returning (items, total_count, total_pages)."""
    # 1. Compute total count using a subquery
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()

    # 2. Slice items with offset and limit
    offset = (params.page - 1) * params.page_size
    paged_stmt = stmt.offset(offset).limit(params.page_size)
    result = await session.execute(paged_stmt)
    items = list(result.scalars().all())

    total_pages = math.ceil(total / params.page_size) if total > 0 else 0
    return items, total, total_pages
