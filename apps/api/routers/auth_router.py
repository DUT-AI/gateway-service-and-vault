from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from core.config.auth import auth_settings
from core.security.deps import get_current_user_payload
from modules.identity.dtos.auth_dtos import (
    TokenResponse,
    UserLoginRequest,
    UserResponse,
)
from modules.identity.services import sso_dutai_service

router = APIRouter(prefix="/api/v1/auth", tags=["Identity"])


@router.post(
    "/sso-login",
    response_model=TokenResponse,
    summary="Authenticate against central DUT-AI SSO IdP",
)
async def sso_login(
    req: UserLoginRequest,
    response: Response,
) -> TokenResponse:
    """Authenticate against DUT-AI Manage SSO Server using email and password."""
    sso_data = await sso_dutai_service.login(email=req.email, password=req.password)
    access_token = sso_data.access_token
    refresh_token = sso_data.refresh_token

    # Set SSO cookies on current host
    response.set_cookie(
        key="access_token",
        value=access_token,
        path="/",
        httponly=True,
        samesite="lax",
    )
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            path="/",
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
    summary="Clear SSO authentication session",
)
async def logout(response: Response) -> dict[str, str]:
    """Clear SSO authentication cookies."""
    for key in ["access_token", "refresh_token"]:
        response.delete_cookie(
            key=key,
            path="/",
            httponly=True,
            samesite="lax",
        )
    return {"message": "Đăng xuất thành công"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get profile of authenticated SSO user",
)
async def get_me(
    payload: Annotated[dict, Depends(get_current_user_payload)],
) -> UserResponse:
    """Retrieve profile of currently authenticated user directly from SSO token."""
    user_id = payload["user_id"]
    return UserResponse(
        id=user_id,
        email=payload.get("email", ""),
        name=payload.get("name"),
        role=payload.get("role", "member"),
        avatar_url=payload.get("avatar_url"),
        status=payload.get("status", "ACTIVE"),
        role_names=payload.get("role_names", []),
        permissions=payload.get("permissions", []),
    )
