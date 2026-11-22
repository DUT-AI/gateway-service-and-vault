import pytest
from sqlalchemy import select

from core.pagination.helpers import paginate_query
from core.pagination.params import PaginationParams
from modules.identity.models.user import UserModel


@pytest.mark.asyncio
async def test_pagination_helper_slices_and_counts(db_session):
    """Verify that paginate_query correctly calculates total, offset, limit, and total_pages."""
    # Seed 15 users
    for i in range(1, 16):
        db_session.add(
            UserModel(
                email=f"user{i:02d}@example.com",
                name=f"User {i:02d}",
                role="user",
                status="ACTIVE",
            )
        )
    await db_session.flush()

    # Query page 1 with page_size 5
    params = PaginationParams(page=1, page_size=5)
    stmt = (
        select(UserModel)
        .where(UserModel.email.startswith("user"))
        .order_by(UserModel.id.asc())
    )
    items, total, total_pages = await paginate_query(db_session, stmt, params)

    assert total == 15
    assert total_pages == 3
    assert len(items) == 5
    assert items[0].email == "user01@example.com"
    assert items[-1].email == "user05@example.com"

    # Query page 3 with page_size 5
    params_page3 = PaginationParams(page=3, page_size=5)
    items3, total3, total_pages3 = await paginate_query(db_session, stmt, params_page3)
    assert total3 == 15
    assert total_pages3 == 3
    assert len(items3) == 5
    assert items3[0].email == "user11@example.com"
    assert items3[-1].email == "user15@example.com"
