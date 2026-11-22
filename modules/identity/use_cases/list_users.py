from core.pagination.params import PaginationParams
from core.pagination.response import PaginatedResponse
from core.utils.datetime_utils import now_utc
from modules.identity.domain.interfaces import IUserRepository
from modules.identity.dtos.auth_dtos import UserResponse


class ListUsersUseCase:
    """Use case to query paginated users with optional search."""

    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    async def execute(
        self, params: PaginationParams
    ) -> PaginatedResponse[UserResponse]:
        users, total, total_pages = await self.user_repo.list_users(
            page=params.page,
            page_size=params.page_size,
            search=params.search,
        )

        items = [
            UserResponse(
                id=u.id,
                email=u.email,
                name=u.name,
                role=u.role,
                avatar_url=u.avatar_url,
                status=u.status,
                created_at=u.created_at or now_utc(),
            )
            for u in users
        ]

        return PaginatedResponse[UserResponse](
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )
