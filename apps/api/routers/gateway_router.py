from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, status

from modules.gateway.domain.entities import ClientType
from modules.gateway.domain.interfaces import IProjectRepository
from modules.gateway.dtos.gateway_dtos import (
    ClientSummaryResponse,
    GenerateVirtualKeyRequest,
    GenerateVirtualKeyResponse,
    ProjectCreateRequest,
    ProjectResponse,
    RegisterClientRequest,
    RegisterClientResponse,
    UpstreamServiceCreateRequest,
    UpstreamServiceResponse,
    VerifyBindingRequest,
    VerifyBindingResponse,
    VirtualKeySummaryResponse,
)
from modules.gateway.use_cases import (
    CreateUpstreamServiceUseCase,
    GenerateVirtualKeyUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    ListRegisteredClientsUseCase,
    ListUpstreamServicesUseCase,
    ListVirtualKeysUseCase,
    ProjectNotFoundError,
    RegisterClientUseCase,
    RevokeVirtualKeyUseCase,
    VerifyIdentityBindingUseCase,
)

router = APIRouter(prefix="/api/v1/gateway", tags=["Gateway"])


# --- Projects Endpoints ---


@router.get(
    "/projects",
    response_model=list[ProjectResponse],
    summary="List all registered projects",
)
@inject
async def list_projects(
    use_case: FromDishka[ListProjectsUseCase],
) -> list[ProjectResponse]:
    """Retrieve all business projects."""
    projects = await use_case.execute()
    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            slug=p.slug,
            description=p.description,
            created_at=p.created_at,
        )
        for p in projects
    ]


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    summary="Get single project by ID",
)
@inject
async def get_project(
    project_id: str,
    use_case: FromDishka[GetProjectUseCase],
) -> ProjectResponse:
    """Retrieve single project by ID."""
    try:
        p = await use_case.execute(project_id)
        return ProjectResponse(
            id=p.id,
            name=p.name,
            slug=p.slug,
            description=p.description,
            created_at=p.created_at,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found",
        )


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new business project",
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


# --- Clients (mTLS Devices & Servers) Endpoints ---


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


# --- Virtual Access Keys Endpoints ---


@router.get(
    "/projects/{project_id}/keys",
    response_model=list[VirtualKeySummaryResponse],
    summary="List virtual keys for a project",
)
@inject
async def list_virtual_keys(
    project_id: str,
    use_case: FromDishka[ListVirtualKeysUseCase],
) -> list[VirtualKeySummaryResponse]:
    """Retrieve all virtual access keys bound to a project."""
    keys = await use_case.execute(project_id)
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
    "/keys/{key_id}/revoke",
    status_code=status.HTTP_200_OK,
    summary="Revoke a virtual access key",
)
@inject
async def revoke_virtual_key(
    key_id: str,
    use_case: FromDishka[RevokeVirtualKeyUseCase],
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


# --- Upstream Services Endpoints ---


@router.get(
    "/services",
    response_model=list[UpstreamServiceResponse],
    summary="List all upstream backend services",
)
@inject
async def list_upstream_services(
    use_case: FromDishka[ListUpstreamServicesUseCase],
) -> list[UpstreamServiceResponse]:
    """Retrieve all registered upstream API services."""
    services = await use_case.execute()
    return [
        UpstreamServiceResponse(
            id=s.id,
            name=s.name,
            slug=s.slug,
            base_url=s.base_url,
            auth_type=s.auth_type,
            timeout_seconds=s.timeout_seconds,
            is_active=s.is_active,
            created_at=s.created_at,
        )
        for s in services
    ]


@router.post(
    "/services",
    response_model=UpstreamServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new upstream backend service",
)
@inject
async def create_upstream_service(
    req: UpstreamServiceCreateRequest,
    use_case: FromDishka[CreateUpstreamServiceUseCase],
) -> UpstreamServiceResponse:
    """Register an upstream API service destination."""
    service = await use_case.execute(
        name=req.name,
        slug=req.slug,
        base_url=req.base_url,
        auth_type=req.auth_type,
        credential=req.credential,
        timeout_seconds=req.timeout_seconds,
    )
    return UpstreamServiceResponse(
        id=service.id,
        name=service.name,
        slug=service.slug,
        base_url=service.base_url,
        auth_type=service.auth_type,
        timeout_seconds=service.timeout_seconds,
        is_active=service.is_active,
        created_at=service.created_at,
    )
