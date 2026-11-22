from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Path

from core.security.deps import get_raw_token
from modules.identity.dtos.user_dtos import UserDetailResponse, UserOptionResponse
from modules.identity.use_cases import (
    GetUserDetailUseCase,
    GetUserOptionsUseCase,
)

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get(
    "/options",
    response_model=list[UserOptionResponse],
    summary="Get all available users for selection options",
)
@inject
async def get_user_options(
    use_case: FromDishka[GetUserOptionsUseCase],
    token: Annotated[str, Depends(get_raw_token)],
) -> list[UserOptionResponse]:
    """Retrieve list of all active organization users from central directory."""
    entities = await use_case.execute(auth_token=token)
    return [
        UserOptionResponse(
            id=u.id,
            name=u.name,
            email=u.email,
            avatar_url=u.avatar_url,
        )
        for u in entities
    ]


@router.get(
    "/{id}",
    response_model=UserDetailResponse,
    summary="Get detailed user profile by integer ID",
)
@inject
async def get_user_by_id(
    id: Annotated[int, Path(..., ge=1, description="Strict user integer identifier")],
    use_case: FromDishka[GetUserDetailUseCase],
    token: Annotated[str, Depends(get_raw_token)],
) -> UserDetailResponse:
    """Retrieve detailed user profile for given integer ID from central directory."""
    entity = await use_case.execute(user_id=id, auth_token=token)
    return UserDetailResponse(
        id=entity.id,
        name=entity.name,
        email=entity.email,
        phone_number=entity.phone_number,
        status=entity.status,
        role_ids=entity.role_ids,
        role_names=entity.role_names,
        permissions=entity.permissions,
        avatar_url=entity.avatar_url,
        discord_id=entity.discord_id,
        zalo_bot_id=entity.zalo_bot_id,
        check_in_card_code_configured=entity.check_in_card_code_configured,
    )
