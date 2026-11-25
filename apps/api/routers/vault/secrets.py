from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Header, Query, status

from apps.api.routers.gateway.access_helpers import ensure_project_access
from core.security.deps import get_optional_user_context
from core.security.roles import UserContext
from modules.gateway.use_cases import CheckProjectMembershipUseCase
from modules.vault.dtos.vault_dtos import (
    CreateSecretRequest,
    GetSecretsResponse,
    ScopeResponse,
    SecretResponse,
)
from modules.vault.use_cases import (
    CreateSecretUseCase,
    GetSecretsByScopeUseCase,
    ListScopesUseCase,
)

router = APIRouter()


@router.post(
    "/projects/{project_id}/secrets",
    response_model=SecretResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_secret(
    project_id: str,
    req: CreateSecretRequest,
    use_case: FromDishka[CreateSecretUseCase],
    membership_uc: FromDishka[CheckProjectMembershipUseCase],
    user_ctx: Annotated[UserContext | None, Depends(get_optional_user_context)] = None,
    x_actor_id: str = Header(default="admin"),
) -> SecretResponse:
    """Create or update an encrypted configuration secret and broadcast change."""
    actor = x_actor_id
    if user_ctx:
        await ensure_project_access(project_id, user_ctx, membership_uc)
        actor = "admin" if user_ctx.is_admin else str(user_ctx.user_id)

    secret = await use_case.execute(
        project_id=project_id,
        scope_name=req.scope_name,
        key=req.key,
        value=req.value,
        actor=actor,
    )
    return SecretResponse(
        id=secret.id,
        project_id=secret.project_id,
        scope_id=secret.scope_id,
        key=secret.key,
        version=secret.version,
        created_at=secret.created_at,
    )


@router.get(
    "/projects/{project_id}/secrets",
    response_model=GetSecretsResponse,
)
@inject
async def get_secrets(
    project_id: str,
    use_case: FromDishka[GetSecretsByScopeUseCase],
    membership_uc: FromDishka[CheckProjectMembershipUseCase],
    scope: str | None = Query(default=None),
    key: str | None = Query(default=None),
    user_ctx: Annotated[UserContext | None, Depends(get_optional_user_context)] = None,
    x_identity_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
) -> GetSecretsResponse:
    """Retrieve decrypted configuration secrets filtered by RoleTier, membership, and key ACL."""
    if user_ctx:
        await ensure_project_access(project_id, user_ctx, membership_uc)
        caller_id = str(user_ctx.user_id)
        bypass_key_acl = user_ctx.is_admin or user_ctx.is_developer
    else:
        caller_id = x_identity_id or x_user_role or "anonymous"
        bypass_key_acl = False

    decrypted_scopes = await use_case.execute(
        project_id=project_id,
        caller_identity_id=caller_id,
        requested_scope=scope,
        requested_key=key,
        bypass_key_acl=bypass_key_acl,
    )
    return GetSecretsResponse(
        project_id=project_id,
        scopes=decrypted_scopes,
    )


@router.get(
    "/projects/{project_id}/scopes",
    response_model=list[ScopeResponse],
    summary="List all secret scopes in a project",
)
@inject
async def list_scopes(
    project_id: str,
    use_case: FromDishka[ListScopesUseCase],
    membership_uc: FromDishka[CheckProjectMembershipUseCase],
    user_ctx: Annotated[UserContext | None, Depends(get_optional_user_context)] = None,
) -> list[ScopeResponse]:
    """Retrieve all secret scopes created within a project."""
    if user_ctx:
        await ensure_project_access(project_id, user_ctx, membership_uc)
    scopes = await use_case.execute(project_id)
    return [
        ScopeResponse(
            id=s.id,
            project_id=s.project_id,
            name=s.name,
            description=s.description,
            created_at=s.created_at,
        )
        for s in scopes
    ]
