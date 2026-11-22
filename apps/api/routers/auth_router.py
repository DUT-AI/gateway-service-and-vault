from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, status

from core.pagination.params import PaginationParams
from core.pagination.response import PaginatedResponse
from core.security.deps import get_current_user_id
from modules.identity.dtos.auth_dtos import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from modules.identity.use_cases import (
    GetCurrentUserUseCase,
    ListUsersUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Identity"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def register(
    req: UserRegisterRequest,
    use_case: FromDishka[RegisterUserUseCase],
) -> UserResponse:
    """Register a new user account."""
    return await use_case.execute(req)


@router.post(
    "/login",
    response_model=TokenResponse,
)
@inject
async def login(
    req: UserLoginRequest,
    use_case: FromDishka[LoginUserUseCase],
) -> TokenResponse:
    """Authenticate with email and password and receive a JWT token."""
    return await use_case.execute(req)


@router.get(
    "/me",
    response_model=UserResponse,
)
@inject
async def get_me(
    user_id: Annotated[int, Depends(get_current_user_id)],
    use_case: FromDishka[GetCurrentUserUseCase],
) -> UserResponse:
    """Retrieve profile of currently authenticated user."""
    return await use_case.execute(user_id)


@router.get(
    "/users",
    response_model=PaginatedResponse[UserResponse],
)
@inject
async def list_users(
    params: Annotated[PaginationParams, Depends()],
    use_case: FromDishka[ListUsersUseCase],
) -> PaginatedResponse[UserResponse]:
    """Retrieve paginated list of registered users."""
    return await use_case.execute(params)
