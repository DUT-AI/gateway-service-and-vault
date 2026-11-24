from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.pagination.helpers import paginate_query
from core.pagination.params import PaginationParams
from modules.identity.domain.entities import UserEntity
from modules.identity.domain.interfaces import IUserRepository
from modules.identity.models.user import UserModel


class SqlUserRepository(IUserRepository):
    """SQLAlchemy implementation of IUserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, model: UserModel) -> UserEntity:
        return UserEntity(
            id=model.id,
            email=model.email,
            name=model.name,
            role=model.role,
            avatar_url=model.avatar_url,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.email == email.lower().strip())
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def create(
        self,
        email: str,
        password_hash: str | None = None,
        name: str | None = None,
        role: str = "user",
    ) -> UserEntity:
        model = UserModel(
            email=email.lower().strip(),
            name=name,
            role=role,
            status="ACTIVE",
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update(self, user: UserEntity) -> UserEntity:
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one()

        model.name = user.name
        model.role = user.role
        model.avatar_url = user.avatar_url
        model.status = user.status

        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
    ) -> tuple[list[UserEntity], int, int]:
        stmt = select(UserModel).order_by(UserModel.id.asc())
        if search:
            search_pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    UserModel.email.ilike(search_pattern),
                    UserModel.name.ilike(search_pattern),
                )
            )

        params = PaginationParams(page=page, page_size=page_size, search=search)
        models, total, total_pages = await paginate_query(self.session, stmt, params)
        entities = [self._to_entity(m) for m in models]
        return entities, total, total_pages
