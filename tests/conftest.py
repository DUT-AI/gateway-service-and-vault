from collections.abc import AsyncIterator

import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.pool import StaticPool

# Import all models to register onto Base.metadata
import core.events.models  # noqa: F401
import modules.gateway.models
import modules.identity.models
import modules.vault.models  # noqa: F401
from apps.api.main import app
from core.database.base import Base
from core.database.unit_of_work import SqlAlchemyUnitOfWork
from core.uow import IUnitOfWork
from modules.gateway.di import GatewayProvider
from modules.identity.di import IdentityProvider
from modules.vault.di import VaultProvider


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


# In-memory SQLite engine for tests with StaticPool
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class TestDatabaseProvider(Provider):
    """Dishka provider for in-memory test database."""

    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return test_engine

    @provide(scope=Scope.APP)
    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        return TestSessionLocal

    @provide(scope=Scope.REQUEST)
    def get_unit_of_work(self, session: AsyncSession) -> IUnitOfWork:
        return SqlAlchemyUnitOfWork(session)

    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        async with TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    """Create all schema tables in in-memory test database and wire test DI container."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    container = make_async_container(
        TestDatabaseProvider(),
        IdentityProvider(),
        GatewayProvider(),
        VaultProvider(),
    )
    setup_dishka(container, app)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """Provide a transactional database session for tests."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Async HTTP client for testing FastAPI endpoints (unauthenticated by default)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def make_auth_headers(
    user_id: int = 1,
    roles: list[str] | None = None,
    email: str = "test@dutai.io.vn",
    permissions: list[str] | None = None,
) -> dict[str, str]:
    """Generate an offline test JWT Authorization header."""
    import jwt

    token = jwt.encode(
        {
            "sub": str(user_id),
            "user_id": user_id,
            "email": email,
            "name": f"Test User {user_id}",
            "roles": roles if roles is not None else ["admin"],
            "permissions": permissions if permissions is not None else [],
        },
        "test-secret-key-at-least-32-bytes-long",
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_client() -> AsyncIterator[AsyncClient]:
    """Async HTTP client pre-authenticated as an SSO Admin user."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers=make_auth_headers(user_id=1, roles=["admin"]),
    ) as ac:
        yield ac
