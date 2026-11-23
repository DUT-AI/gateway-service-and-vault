from typing import Annotated, Any

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Path, status

from modules.identity.use_cases.sync_sso_user_revocation import (
    SyncSsoUserRevocationUseCase,
)

router = APIRouter(prefix="/api/v1/identity", tags=["Identity"])


@router.post(
    "/users/{user_id}/sync-revocation",
    status_code=status.HTTP_200_OK,
    summary="Cascade revoke all clients and virtual keys of deactivated SSO user",
)
@inject
async def sync_sso_user_revocation(
    user_id: Annotated[
        int, Path(..., ge=1, description="Strict user integer identifier")
    ],
    use_case: FromDishka[SyncSsoUserRevocationUseCase],
) -> dict[str, Any]:
    """Cascade revoke all registered clients and active virtual keys owned by an SSO user."""
    return await use_case.execute(user_id=user_id)
