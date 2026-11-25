from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Header, Query, status

from core.security.deps import require_role_tier
from core.security.roles import RoleTier, UserContext
from modules.vault.dtos.vault_dtos import (
    GrantKeyPermissionRequest,
    IdentityPermissionsResponse,
    KeyPermissionResponse,
)
from modules.vault.use_cases import (
    GrantKeyPermissionUseCase,
    ListIdentityPermissionsUseCase,
    RevokeKeyPermissionUseCase,
)

router = APIRouter()


@router.post(
    "/projects/{project_id}/permissions",
    response_model=KeyPermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def grant_key_permission(
    project_id: str,
    req: GrantKeyPermissionRequest,
    use_case: FromDishka[GrantKeyPermissionUseCase],
    admin_ctx: Annotated[UserContext, Depends(require_role_tier(RoleTier.ADMIN))],
    x_actor_id: str = Header(default="admin"),
) -> KeyPermissionResponse:
    """Grant an identity read permission for a secret key (Admin only)."""
    granted_by = admin_ctx.email or str(admin_ctx.user_id) or x_actor_id
    perm = await use_case.execute(
        project_id=project_id,
        identity_id=req.identity_id,
        secret_key=req.secret_key,
        identity_type=req.identity_type,
        granted_by=granted_by,
    )
    return KeyPermissionResponse(
        id=perm.id,
        project_id=perm.project_id,
        identity_id=perm.identity_id,
        identity_type=perm.identity_type,
        secret_key=perm.secret_key,
        granted_by=perm.granted_by,
        created_at=perm.created_at,
    )


@router.delete(
    "/projects/{project_id}/permissions",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def revoke_key_permission(
    project_id: str,
    use_case: FromDishka[RevokeKeyPermissionUseCase],
    _: Annotated[UserContext, Depends(require_role_tier(RoleTier.ADMIN))],
    identity_id: str = Query(..., min_length=1),
    secret_key: str = Query(..., min_length=1),
    x_actor_id: str = Header(default="admin"),
) -> None:
    """Revoke an identity's read permission for a secret key."""
    await use_case.execute(
        project_id=project_id,
        identity_id=identity_id,
        secret_key=secret_key,
    )


@router.get(
    "/projects/{project_id}/permissions",
    response_model=IdentityPermissionsResponse,
)
@inject
async def list_identity_permissions(
    project_id: str,
    use_case: FromDishka[ListIdentityPermissionsUseCase],
    identity_id: str = Query(..., min_length=1),
) -> IdentityPermissionsResponse:
    """List all permitted secret keys for an identity in a project."""
    permitted_keys = await use_case.execute(
        project_id=project_id,
        identity_id=identity_id,
    )
    return IdentityPermissionsResponse(
        project_id=project_id,
        identity_id=identity_id,
        permitted_keys=permitted_keys,
    )
