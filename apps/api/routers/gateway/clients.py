from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, status

from modules.gateway.domain.entities import ClientType
from modules.gateway.dtos.gateway_dtos import (
    ClientSummaryResponse,
    RegisterClientRequest,
    RegisterClientResponse,
    RevokeClientResponse,
)
from modules.gateway.use_cases import (
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
) -> list[ClientSummaryResponse]:
    """Retrieve all registered device and machine client identities."""
    clients = await use_case.execute()
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
) -> RegisterClientResponse:
    """Issue a private mTLS client certificate and register the client identity."""
    client_type = ClientType(req.client_type.upper())
    client, cert = await use_case.execute(
        name=req.name,
        client_type=client_type,
        owner_id=req.owner_id,
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
) -> RevokeClientResponse:
    """Revoke a registered client and all active virtual keys bound to it."""
    success = await use_case.execute(client_id)
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
