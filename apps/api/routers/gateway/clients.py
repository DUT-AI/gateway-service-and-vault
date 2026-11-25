from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, status

from core.security.deps import get_current_user_context
from core.security.roles import UserContext
from modules.gateway.domain.entities import ClientType
from modules.gateway.dtos.gateway_dtos import (
    ClientSummaryResponse,
    RegisterClientRequest,
    RegisterClientResponse,
    RevokeClientResponse,
)
from modules.gateway.use_cases import (
    ClientOwnershipDeniedError,
    ListRegisteredClientsUseCase,
    RegisterClientUseCase,
    RevokeClientUseCase,
)

router = APIRouter()


@router.get(
    "/clients",
    response_model=list[ClientSummaryResponse],
    summary="List all registered client identities",
)
@inject
async def list_clients(
    use_case: FromDishka[ListRegisteredClientsUseCase],
    user_ctx: Annotated[UserContext, Depends(get_current_user_context)],
) -> list[ClientSummaryResponse]:
    """Retrieve registered device and machine client identities (all for Admin, own for others)."""
    clients = await use_case.execute(
        owner_id=str(user_ctx.user_id),
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


@router.post(
    "/clients",
    response_model=RegisterClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a client and issue mTLS certificate",
)
@inject
async def register_client(
    req: RegisterClientRequest,
    use_case: FromDishka[RegisterClientUseCase],
    user_ctx: Annotated[UserContext, Depends(get_current_user_context)],
) -> RegisterClientResponse:
    """Issue a self-owned mTLS client certificate and register the client identity."""
    client_type = ClientType(req.client_type.upper())
    if user_ctx.is_other and client_type != ClientType.USER_DEVICE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản của bạn chỉ được phép đăng ký thiết bị cá nhân (USER_DEVICE)",
        )
    client, cert = await use_case.execute(
        name=req.name,
        client_type=client_type,
        owner_id=str(user_ctx.user_id),
        validity_days=req.validity_days,
    )
    return RegisterClientResponse(
        id=client.id,
        name=client.name,
        client_type=client.client_type.value,
        owner_id=client.owner_id,
        cert_fingerprint=client.cert_fingerprint,
        cert_serial=client.cert_serial,
        cert_pem=cert.cert_pem,
        key_pem=cert.key_pem,
        expires_at=client.expires_at,
    )


@router.post(
    "/clients/{client_id}/revoke",
    response_model=RevokeClientResponse,
    summary="Revoke a registered client hardware device",
)
@inject
async def revoke_client(
    client_id: str,
    use_case: FromDishka[RevokeClientUseCase],
    user_ctx: Annotated[UserContext, Depends(get_current_user_context)],
) -> RevokeClientResponse:
    """Revoke a registered client and all active virtual keys bound to it."""
    try:
        success = await use_case.execute(
            client_id=client_id,
            caller_owner_id=str(user_ctx.user_id),
            is_admin=user_ctx.is_admin,
        )
    except ClientOwnershipDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client '{client_id}' not found",
        )
    return RevokeClientResponse(
        message="Client and all associated virtual keys revoked successfully",
        client_id=client_id,
        is_revoked=True,
    )
