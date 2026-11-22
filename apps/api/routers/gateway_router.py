from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status

from modules.gateway.domain.entities import ClientType
from modules.gateway.domain.interfaces import IProjectRepository
from modules.gateway.dtos.gateway_dtos import (
    GenerateVirtualKeyRequest,
    GenerateVirtualKeyResponse,
    ProjectCreateRequest,
    ProjectResponse,
    RegisterClientRequest,
    RegisterClientResponse,
    VerifyBindingRequest,
    VerifyBindingResponse,
)
from modules.gateway.use_cases import (
    GenerateVirtualKeyUseCase,
    RegisterClientUseCase,
    VerifyIdentityBindingUseCase,
)

router = APIRouter(prefix="/api/v1/gateway", tags=["Gateway"])


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_project(
    req: ProjectCreateRequest,
    project_repo: FromDishka[IProjectRepository],
) -> ProjectResponse:
    """Create a new business project."""
    project = await project_repo.create(
        name=req.name,
        slug=req.slug,
        description=req.description,
    )
    return ProjectResponse(
        id=project.id,
        name=project.name,
        slug=project.slug,
        description=project.description,
        created_at=project.created_at,
    )


@router.post(
    "/clients",
    response_model=RegisterClientResponse,
    status_code=status.HTTP_201_CREATED,
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
    "/keys",
    response_model=GenerateVirtualKeyResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def generate_virtual_key(
    req: GenerateVirtualKeyRequest,
    use_case: FromDishka[GenerateVirtualKeyUseCase],
) -> GenerateVirtualKeyResponse:
    """Generate a Virtual Access Key bound to a registered client and project."""
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
    "/verify-binding",
    response_model=VerifyBindingResponse,
)
@inject
async def verify_binding(
    req: VerifyBindingRequest,
    use_case: FromDishka[VerifyIdentityBindingUseCase],
) -> VerifyBindingResponse:
    """Verify identity binding between virtual key and mTLS client certificate."""
    await use_case.execute(
        raw_virtual_key=req.raw_virtual_key,
        cert_fingerprint=req.cert_fingerprint,
        project_id=req.project_id,
    )
    return VerifyBindingResponse(
        valid=True,
        message="Identity binding verified successfully",
    )
