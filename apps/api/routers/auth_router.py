from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Response, status

from core.config.auth import auth_settings
from core.pagination.params import PaginationParams
from core.pagination.response import PaginatedResponse
from core.security.deps import get_current_user_payload
from modules.identity.dtos.auth_dtos import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from modules.identity.services import sso_dutai_service
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
    response: Response,
    use_case: FromDishka[LoginUserUseCase],
) -> TokenResponse:
    """Authenticate with email and password and receive a JWT token."""
    token_resp = await use_case.execute(req)
    response.set_cookie(
        key="access_token",
        value=token_resp.access_token,
        max_age=token_resp.expires_in,
        path="/",
        httponly=True,
        samesite="lax",
    )
    return token_resp


@router.post(
    "/sso-login",
    response_model=TokenResponse,
)
async def sso_login(
    req: UserLoginRequest,
    response: Response,
) -> TokenResponse:
    """Authenticate against DUT-AI Manage SSO Server using email and password."""
    sso_data = await sso_dutai_service.login(email=req.email, password=req.password)
    access_token = sso_data.access_token
    refresh_token = sso_data.refresh_token

    # Set SSO cookies (both on .dutai.io.vn and host)
    for domain in [".dutai.io.vn", None]:
        response.set_cookie(
            key="access_token",
            value=access_token,
            path="/",
            domain=domain,
            httponly=True,
            samesite="lax",
        )
        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                path="/",
                domain=domain,
                httponly=True,
                samesite="lax",
            )

    return TokenResponse(
        access_token=access_token,
        token_type=sso_data.token_type or "bearer",
        expires_in=sso_data.expires_in
        or (auth_settings.access_token_expire_minutes * 60),
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(response: Response) -> dict[str, str]:
    """Clear SSO authentication cookies on both .dutai.io.vn and local domain."""
    for domain in [".dutai.io.vn", None]:
        for key in ["access_token", "refresh_token"]:
            response.delete_cookie(
                key=key,
                path="/",
                domain=domain,
                httponly=True,
                samesite="lax",
            )
    return {"message": "Đăng xuất thành công"}


@router.get(
    "/me",
    response_model=UserResponse,
)
@inject
async def get_me(
    payload: Annotated[dict, Depends(get_current_user_payload)],
    use_case: FromDishka[GetCurrentUserUseCase],
) -> UserResponse:
    """Retrieve profile of currently authenticated user."""
    # Nếu là SSO User từ Manage IdP, trả về trực tiếp thông tin từ token/SSO profile
    if payload.get("is_sso"):
        return UserResponse(
            id=int(payload["user_id"]),
            email=payload.get("email", ""),
            name=payload.get("name"),
            role=payload.get("role", "member"),
            avatar_url=payload.get("avatar_url"),
            status="ACTIVE",
            role_names=payload.get("role_names", []),
            permissions=payload.get("permissions", []),
        )

    # Nếu là local account, truy vấn thông qua use_case từ database
    user_id_raw = payload.get("sub") or payload.get("user_id")
    user_id = int(str(user_id_raw)) if user_id_raw is not None else 0
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
