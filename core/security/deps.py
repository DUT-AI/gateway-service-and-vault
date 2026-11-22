from typing import Annotated

from fastapi import Cookie, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.exceptions import UnauthorizedError
from core.security.jwt import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    access_token: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> dict:
    """Extract and validate current authenticated user payload from Bearer token or Cookie."""
    token = None
    if credentials:
        token = credentials.credentials
    elif access_token:
        token = access_token

    if not token:
        raise UnauthorizedError(
            "Missing authentication token in Authorization header or access_token cookie"
        )

    payload = decode_access_token(token)
    return payload


async def get_current_user_id(
    payload: Annotated[dict, Depends(get_current_user_payload)],
) -> int:
    """Extract integer user_id from token sub or user_id claim."""
    sub = payload.get("user_id") or payload.get("sub")
    if sub is None:
        raise UnauthorizedError("Token payload does not contain subject ID")
    try:
        return int(sub)
    except (ValueError, TypeError) as e:
        raise UnauthorizedError("Invalid user subject format in token") from e
