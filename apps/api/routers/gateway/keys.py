from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Request, status

from apps.api.routers.gateway.access_helpers import ensure_project_access
from core.security.deps import get_current_user_context, require_role_tier
from core.security.roles import RoleTier, UserContext
from modules.gateway.dtos.gateway_dtos import (
    ClientSummaryResponse,
    GenerateVirtualKeyRequest,
    GenerateVirtualKeyResponse,
    VerifyBindingRequest,
    VerifyBindingResponse,
    VirtualKeySummaryResponse,
)
from modules.gateway.use_cases import (
    CheckProjectMembershipUseCase,
    GenerateVirtualKeyUseCase,
    ListProjectAvailableClientsUseCase,
    ListVirtualKeysUseCase,
    RevokeVirtualKeyUseCase,
    VerifyIdentityBindingUseCase,
)

router = APIRouter()


@router.get(
    "/projects/{project_id}/available-clients",
    response_model=list[ClientSummaryResponse],
    summary="List active mTLS clients of project members eligible for Virtual Key binding",
)
@inject
async def list_project_available_clients(
    project_id: str,
    use_case: FromDishka[ListProjectAvailableClientsUseCase],
    membership_uc: FromDishka[CheckProjectMembershipUseCase],
    user_ctx: Annotated[
        UserContext,
        Depends(require_role_tier(RoleTier.ADMIN, RoleTier.PROJECT_DEVELOPER)),
    ],
) -> list[ClientSummaryResponse]:
    """Retrieve active mTLS clients belonging to members of the project (or all for Admin)."""
    await ensure_project_access(project_id, user_ctx, membership_uc)
    clients = await use_case.execute(
        project_id=project_id,
        caller_owner_id=str(user_ctx.user_id),
        is_admin=user_ctx.is_admin,
    )
    return [
        ClientSummaryResponse(
            id=c.id,
            name=c.name,
            client_type=c.client_type.value,
            owner_id=c.owner_id,
            cert_fingerprint=c.cert_fingerprint,
            cert_serial=c.cert_serial,
            expires_at=c.expires_at,
            is_revoked=c.is_revoked,
            created_at=c.created_at,
        )
        for c in clients
    ]


@router.get(
    "/projects/{project_id}/keys",
    response_model=list[VirtualKeySummaryResponse],
    summary="List virtual keys for a project",
)
@inject
async def list_virtual_keys(
    project_id: str,
    use_case: FromDishka[ListVirtualKeysUseCase],
    membership_uc: FromDishka[CheckProjectMembershipUseCase],
    user_ctx: Annotated[UserContext, Depends(get_current_user_context)],
) -> list[VirtualKeySummaryResponse]:
    """Retrieve virtual access keys bound to a project (read-only own-device keys for Tier 3)."""
    await ensure_project_access(project_id, user_ctx, membership_uc)
    owner_filter = str(user_ctx.user_id) if user_ctx.is_other else None
    keys = await use_case.execute(project_id, owner_id_filter=owner_filter)
    return [
        VirtualKeySummaryResponse(
            id=k.id,
            client_id=k.client_id,
            project_id=k.project_id,
            key_prefix=k.key_prefix,
            status=k.status.value,
            created_at=k.created_at,
            revoked_at=k.revoked_at,
        )
        for k in keys
    ]


@router.post(
    "/keys",
    response_model=GenerateVirtualKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a Virtual Access Key bound to a client and project",
)
@inject
async def generate_virtual_key(
    req: GenerateVirtualKeyRequest,
    use_case: FromDishka[GenerateVirtualKeyUseCase],
    membership_uc: FromDishka[CheckProjectMembershipUseCase],
    user_ctx: Annotated[
        UserContext,
        Depends(require_role_tier(RoleTier.ADMIN, RoleTier.PROJECT_DEVELOPER)),
    ],
) -> GenerateVirtualKeyResponse:
    """Generate a Virtual Access Key bound to a registered client and project."""
    await ensure_project_access(req.project_id, user_ctx, membership_uc)
    key_entity, raw_token = await use_case.execute(
        client_id=req.client_id,
        project_id=req.project_id,
    )
    return GenerateVirtualKeyResponse(
        id=key_entity.id,
        client_id=key_entity.client_id,
        project_id=key_entity.project_id,
        virtual_key=raw_token,
        key_prefix=key_entity.key_prefix,
        status=key_entity.status.value,
        created_at=key_entity.created_at,
    )


@router.post(
    "/keys/{key_id}/revoke",
    status_code=status.HTTP_200_OK,
    summary="Revoke a virtual access key",
)
@inject
async def revoke_virtual_key(
    key_id: str,
    use_case: FromDishka[RevokeVirtualKeyUseCase],
    _: Annotated[
        UserContext,
        Depends(require_role_tier(RoleTier.ADMIN, RoleTier.PROJECT_DEVELOPER)),
    ],
) -> dict[str, str]:
    """Revoke a compromised or obsolete virtual access key."""
    success = await use_case.execute(key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Key '{key_id}' not found or already revoked",
        )
    return {"message": "Virtual key revoked successfully"}


@router.post(
    "/verify-binding",
    response_model=VerifyBindingResponse,
    summary="Verify identity binding between virtual key and certificate",
)
@inject
async def verify_binding(
    req: VerifyBindingRequest,
    use_case: FromDishka[VerifyIdentityBindingUseCase],
    request: Request,
) -> VerifyBindingResponse:
    """Verify identity binding between virtual key and mTLS client certificate."""
    client_ip = req.client_ip or (request.client.host if request.client else None)
    await use_case.execute(
        raw_virtual_key=req.raw_virtual_key,
        cert_fingerprint=req.cert_fingerprint,
        project_id=req.project_id,
        service_id=req.service_id,
        service_slug=req.service_slug,
        client_raw_cert=req.client_raw_cert,
        client_signature=req.client_signature,
        client_timestamp=req.client_timestamp,
        request_method=req.request_method,
        request_path=req.request_path,
        client_ip=client_ip,
    )
    return VerifyBindingResponse(
        valid=True,
        message="Identity binding verified successfully",
    )
