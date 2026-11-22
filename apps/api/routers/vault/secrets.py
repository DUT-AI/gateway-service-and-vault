from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Header, Query, status

from modules.vault.dtos.vault_dtos import (
    CreateSecretRequest,
    GetSecretsResponse,
    SecretResponse,
)
from modules.vault.use_cases import (
    CreateSecretUseCase,
    GetSecretsByScopeUseCase,
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
    x_actor_id: str = Header(default="admin"),
) -> SecretResponse:
    """Create or update an encrypted configuration secret and broadcast change."""
    secret = await use_case.execute(
        project_id=project_id,
        scope_name=req.scope_name,
        key=req.key,
        value=req.value,
        actor=x_actor_id,
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
    x_identity_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
) -> GetSecretsResponse:
    """Retrieve decrypted configuration secrets filtered by identity permissions."""
    caller_id = x_identity_id or x_user_role or "anonymous"
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
