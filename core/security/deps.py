from typing import Annotated

from fastapi import Cookie, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.exceptions import UnauthorizedError
from core.security.jwt import decode_access_token
from modules.identity.services.sso_service import sso_dutai_service

bearer_scheme = HTTPBearer(auto_error=False)


async def get_raw_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    access_token: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> str:
    """Extract raw token string from Bearer credentials or access_token cookie."""
    token = None
    if credentials:
        token = credentials.credentials
    elif access_token:
        token = access_token

    if not token:
        raise UnauthorizedError(
            "Missing authentication token in Authorization header or access_token cookie"
        )
    return token


async def get_current_user_payload(
    token: Annotated[str, Depends(get_raw_token)],
) -> dict:
    """Extract and validate current authenticated user payload.

    1. First tries local JWT verification (for local accounts).
    2. If local signature fails, validates against DUT AI Manage SSO (/api/v1/auth/me).
    """
    try:
        payload = decode_access_token(token)
        return payload
    except UnauthorizedError:
        # Validate against DUT-AI Manage IdP
        pass

    sso_user = await sso_dutai_service.get_current_user(token)
    if sso_user:
        return {
            "sub": str(sso_user.id),
            "user_id": sso_user.id,
            "name": sso_user.name,
            "email": sso_user.email,
            "role": (sso_user.role_names or ["member"])[0],
            "role_names": sso_user.role_names,
            "permissions": sso_user.permissions,
            "avatar_url": sso_user.avatar_url,
            "is_sso": True,
        }

    raise UnauthorizedError(
        "Token xác thực không hợp lệ hoặc đã hết hạn trên SSO Manage"
    )


async def get_current_user_id(
    payload: Annotated[dict, Depends(get_current_user_payload)],
) -> int:
    """Extract integer user_id from token sub or user_id claim."""
    sub = payload.get("sub") or payload.get("user_id") or payload.get("id")
    if sub is None:
        raise UnauthorizedError("Token payload does not contain subject ID")
    try:
        return int(sub)
    except (ValueError, TypeError) as e:
        raise UnauthorizedError("Invalid user subject format in token") from e
