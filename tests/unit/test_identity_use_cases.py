from datetime import UTC, datetime

import pytest

from core.security.password import hash_password
from modules.identity.domain.entities import UserEntity
from modules.identity.domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from modules.identity.domain.interfaces import IUserRepository
from modules.identity.dtos.auth_dtos import (
    UserLoginRequest,
    UserRegisterRequest,
)
from modules.identity.use_cases import (
    GetCurrentUserUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
)


class InMemoryUserRepository(IUserRepository):
    """In-memory repository for isolated unit testing."""

    def __init__(self) -> None:
        self.users: dict[int, UserEntity] = {}
        self._current_id = 1

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        return self.users.get(user_id)

    async def get_by_email(self, email: str) -> UserEntity | None:
        for u in self.users.values():
            if u.email.lower() == email.lower():
                return u
        return None

    async def create(
        self,
        email: str,
        password_hash: str,
        name: str | None = None,
        role: str = "user",
    ) -> UserEntity:
        user = UserEntity(
            id=self._current_id,
            email=email,
            password_hash=password_hash,
            name=name,
            role=role,
            status="ACTIVE",
            created_at=datetime.now(UTC),
        )
        self.users[self._current_id] = user
        self._current_id += 1
        return user

    async def update(self, user: UserEntity) -> UserEntity:
        self.users[user.id] = user
        return user


@pytest.mark.asyncio
async def test_register_user_success():
    repo = InMemoryUserRepository()
    uc = RegisterUserUseCase(repo)

    req = UserRegisterRequest(
        email="newuser@example.com",
        password="SuperSecurePassword123!",
        name="New User",
    )
    res = await uc.execute(req)

    assert res.id == 1
    assert res.email == "newuser@example.com"
    assert res.name == "New User"
    assert res.role == "user"


@pytest.mark.asyncio
async def test_register_duplicate_email_raises():
    repo = InMemoryUserRepository()
    uc = RegisterUserUseCase(repo)

    req = UserRegisterRequest(
        email="duplicate@example.com",
        password="SuperSecurePassword123!",
    )
    await uc.execute(req)

    with pytest.raises(UserAlreadyExistsError):
        await uc.execute(req)


@pytest.mark.asyncio
async def test_login_user_success_and_failure():
    repo = InMemoryUserRepository()
    pwd_hash = hash_password("MyPassword123!")
    await repo.create(email="login@example.com", password_hash=pwd_hash)

    login_uc = LoginUserUseCase(repo)

    # Success
    res = await login_uc.execute(
        UserLoginRequest(email="login@example.com", password="MyPassword123!")
    )
    assert res.access_token is not None
    assert res.token_type == "bearer"
    assert res.expires_in > 0

    # Wrong password
    with pytest.raises(InvalidCredentialsError):
        await login_uc.execute(
            UserLoginRequest(email="login@example.com", password="WrongPassword!")
        )

    # Non-existent user
    with pytest.raises(InvalidCredentialsError):
        await login_uc.execute(
            UserLoginRequest(email="notfound@example.com", password="MyPassword123!")
        )


@pytest.mark.asyncio
async def test_get_current_user():
    repo = InMemoryUserRepository()
    user = await repo.create(
        email="profile@example.com",
        password_hash="anyhash",
        name="Profile User",
    )

    uc = GetCurrentUserUseCase(repo)
    profile = await uc.execute(user.id)
    assert profile.email == "profile@example.com"
    assert profile.name == "Profile User"

    with pytest.raises(UserNotFoundError):
        await uc.execute(9999)
