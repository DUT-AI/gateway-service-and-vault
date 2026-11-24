from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Header, Query, status

from apps.api.routers.vault.auth_helpers import resolve_caller_identity
from core.security.deps import get_optional_user_payload
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
    user_payload: Annotated[dict | None, Depends(get_optional_user_payload)] = None,
    x_actor_id: str = Header(default="admin"),
) -> SecretResponse:
    """Create or update an encrypted configuration secret and broadcast change."""
    actor = x_actor_id
    if user_payload and x_actor_id == "admin":
        actor = user_payload.get("email") or str(user_payload.get("user_id")) or "admin"

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
    scope: str | None = Query(default=None),
    key: str | None = Query(default=None),
    user_payload: Annotated[dict | None, Depends(get_optional_user_payload)] = None,
    x_identity_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
) -> GetSecretsResponse:
    """Retrieve decrypted configuration secrets filtered by identity permissions."""
    caller_id = resolve_caller_identity(user_payload, x_identity_id, x_user_role)
    decrypted_scopes = await use_case.execute(
        project_id=project_id,
        caller_identity_id=caller_id,
        requested_scope=scope,
        requested_key=key,
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
) -> list[ScopeResponse]:
    """Retrieve all secret scopes created within a project."""
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
