import pytest
from sqlalchemy import select

from core.pagination.helpers import paginate_query
from core.pagination.params import PaginationParams
from modules.gateway.models.project import ProjectModel


@pytest.mark.asyncio
async def test_pagination_helper_slices_and_counts(db_session):
    """Verify that paginate_query correctly calculates total, offset, limit, and total_pages."""
    # Seed 15 projects
    for i in range(1, 16):
        db_session.add(
            ProjectModel(
                id=f"proj_page_{i:02d}",
                name=f"Project {i:02d}",
                slug=f"proj-{i:02d}",
                description=f"Pagination test project {i:02d}",
            )
        )
    await db_session.flush()

    # Query page 1 with page_size 5
    params = PaginationParams(page=1, page_size=5)
    stmt = (
        select(ProjectModel)
        .where(ProjectModel.slug.startswith("proj-"))
        .order_by(ProjectModel.slug.asc())
    )
    items, total, total_pages = await paginate_query(db_session, stmt, params)

    assert total == 15
    assert total_pages == 3
    assert len(items) == 5
    assert items[0].slug == "proj-01"
    assert items[-1].slug == "proj-05"

    # Query page 3 with page_size 5
    params_page3 = PaginationParams(page=3, page_size=5)
    items3, total3, total_pages3 = await paginate_query(db_session, stmt, params_page3)
    assert total3 == 15
    assert total_pages3 == 3
    assert len(items3) == 5
    assert items3[0].slug == "proj-11"
    assert items3[-1].slug == "proj-15"
