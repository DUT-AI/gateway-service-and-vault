from datetime import datetime

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, Query, Request, status

from modules.gateway.domain.entities import ClientType
from modules.gateway.domain.interfaces import (
    IProjectRepository,
    IQuotaUsageTracker,
    IUpstreamServiceRepository,
)
from modules.gateway.dtos.audit_dtos import (
    AuditEventListResponse,
    AuditEventResponse,
    SecurityAlertItemResponse,
    SecurityAlertsResponse,
)
from modules.gateway.dtos.gateway_dtos import (
    BindServiceToProjectRequest,
    ClientSummaryResponse,
    GenerateVirtualKeyRequest,
    GenerateVirtualKeyResponse,
    ProjectAllowedServiceResponse,
    ProjectCreateRequest,
    ProjectResponse,
    QuotaUsageResponse,
    RegisterClientRequest,
    RegisterClientResponse,
    RevokeClientResponse,
    UpdateServiceQuotaRequest,
    UpstreamServiceCreateRequest,
    UpstreamServiceResponse,
    VerifyBindingRequest,
    VerifyBindingResponse,
    VirtualKeySummaryResponse,
)
from modules.gateway.use_cases import (
    BindServiceToProjectUseCase,
    CreateUpstreamServiceUseCase,
    GenerateVirtualKeyUseCase,
    GetProjectServiceUsageUseCase,
    GetProjectUseCase,
    GetSecurityAlertsUseCase,
    ListAuditEventsUseCase,
    ListProjectAllowedServicesUseCase,
    ListProjectsUseCase,
    ListRegisteredClientsUseCase,
    ListUpstreamServicesUseCase,
    ListVirtualKeysUseCase,
    ProjectNotFoundError,
    RegisterClientUseCase,
    RevokeClientUseCase,
    RevokeVirtualKeyUseCase,
    ServiceAlreadyBoundError,
    ServiceNotBoundError,
    ServiceNotFoundError,
    UnbindServiceFromProjectUseCase,
    UpdateProjectServiceQuotaUseCase,
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
        client_ip=client_ip,
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


# --- Project Upstream Service Binding & Quota Endpoints ---


@router.get(
    "/projects/{project_id}/services",
    response_model=list[ProjectAllowedServiceResponse],
    summary="List all allowed upstream services and quota for a project",
)
@inject
async def list_project_allowed_services(
    project_id: str,
    use_case: FromDishka[ListProjectAllowedServicesUseCase],
    quota_tracker: FromDishka[IQuotaUsageTracker],
) -> list[ProjectAllowedServiceResponse]:
    """Retrieve all upstream services bound to this project with their quota policies and usage."""
    try:
        items = await use_case.execute(project_id)
        results = []
        for svc, quota in items:
            daily = quota.quota_daily if quota else 10000
            usage = await quota_tracker.get_usage(project_id, svc.id)
            pct = round((usage / daily) * 100, 1) if daily > 0 else 0.0
            results.append(
                ProjectAllowedServiceResponse(
                    service_id=svc.id,
                    service_name=svc.name,
                    service_slug=svc.slug,
                    base_url=svc.base_url,
                    auth_type=svc.auth_type,
                    is_service_active=svc.is_active,
                    rate_limit_rpm=quota.rate_limit_rpm if quota else 60,
                    quota_daily=daily,
                    is_quota_active=quota.is_active if quota else True,
                    usage_today=usage,
                    usage_percentage=pct,
                    bound_at=quota.created_at if quota else svc.created_at,
                )
            )
        return results
    except ProjectNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/projects/{project_id}/services/{service_id}/usage",
    response_model=QuotaUsageResponse,
    summary="Get real-time daily quota usage for a service in a project",
)
@inject
async def get_project_service_usage(
    project_id: str,
    service_id: str,
    use_case: FromDishka[GetProjectServiceUsageUseCase],
) -> QuotaUsageResponse:
    """Retrieve today's request usage count and quota consumption percentage."""
    return await use_case.execute(project_id, service_id)


@router.post(
    "/projects/{project_id}/services",
    response_model=ProjectAllowedServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bind an upstream service to a project with quota policy",
)
@inject
async def bind_service_to_project(
    project_id: str,
    req: BindServiceToProjectRequest,
    use_case: FromDishka[BindServiceToProjectUseCase],
) -> ProjectAllowedServiceResponse:
    """Authorize an upstream service for a project with defined rate limit and daily quota."""
    try:
        svc, quota = await use_case.execute(
            project_id=project_id,
            service_id=req.service_id,
            rate_limit_rpm=req.rate_limit_rpm,
            quota_daily=req.quota_daily,
        )
        return ProjectAllowedServiceResponse(
            service_id=svc.id,
            service_name=svc.name,
            service_slug=svc.slug,
            base_url=svc.base_url,
            auth_type=svc.auth_type,
            is_service_active=svc.is_active,
            rate_limit_rpm=quota.rate_limit_rpm,
            quota_daily=quota.quota_daily,
            is_quota_active=quota.is_active,
            bound_at=quota.created_at,
        )
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceAlreadyBoundError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.put(
    "/projects/{project_id}/services/{service_id}/quota",
    response_model=ProjectAllowedServiceResponse,
    summary="Update quota policy for a bound project service",
)
@inject
async def update_project_service_quota(
    project_id: str,
    service_id: str,
    req: UpdateServiceQuotaRequest,
    use_case: FromDishka[UpdateProjectServiceQuotaUseCase],
    service_repo: FromDishka[IUpstreamServiceRepository],
) -> ProjectAllowedServiceResponse:
    """Update rate limit RPM or daily quota for a project-service binding."""
    try:
        quota = await use_case.execute(
            project_id=project_id,
            service_id=service_id,
            rate_limit_rpm=req.rate_limit_rpm,
            quota_daily=req.quota_daily,
        )
        svc = await service_repo.get_by_id(service_id)
        if not svc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Upstream service '{service_id}' not found",
            )
        return ProjectAllowedServiceResponse(
            service_id=svc.id,
            service_name=svc.name,
            service_slug=svc.slug,
            base_url=svc.base_url,
            auth_type=svc.auth_type,
            is_service_active=svc.is_active,
            rate_limit_rpm=quota.rate_limit_rpm,
            quota_daily=quota.quota_daily,
            is_quota_active=quota.is_active,
            bound_at=quota.created_at,
        )
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceNotBoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/projects/{project_id}/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke/unbind an upstream service from a project",
)
@inject
async def unbind_service_from_project(
    project_id: str,
    service_id: str,
    use_case: FromDishka[UnbindServiceFromProjectUseCase],
) -> None:
    """Revoke a project's access to an upstream service and delete its quota policy."""
    try:
        await use_case.execute(project_id, service_id)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceNotBoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Audit Events & Security Alerts Endpoints ---


@router.get(
    "/audit-events",
    response_model=AuditEventListResponse,
    summary="Query audit log records with filters and pagination",
)
@inject
async def list_audit_events(
    use_case: FromDishka[ListAuditEventsUseCase],
    project_id: str | None = None,
    client_type: str | None = None,
    decision: str | None = None,
    action: str | None = None,
    error_code: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AuditEventListResponse:
    """Query immutable security audit logs with filtering and pagination."""
    events, total = await use_case.execute(
        project_id=project_id,
        client_type=client_type,
        decision=decision,
        action=action,
        error_code=error_code,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return AuditEventListResponse(
        items=[
            AuditEventResponse(
                id=e.id,
                timestamp=e.timestamp,
                client_type=(
                    e.client_type.value
                    if hasattr(e.client_type, "value")
                    else str(e.client_type)
                ),
                actor_id=e.actor_id,
                project_id=e.project_id,
                service_id=e.service_id,
                action=e.action,
                decision=e.decision,
                client_ip=e.client_ip,
                error_code=e.error_code,
                metadata=e.metadata,
            )
            for e in events
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/security-alerts",
    response_model=SecurityAlertsResponse,
    summary="Retrieve active security anomaly alerts",
)
@inject
async def get_security_alerts(
    use_case: FromDishka[GetSecurityAlertsUseCase],
    window_minutes: int = Query(default=5, ge=1, le=60),
    threshold: int = Query(default=3, ge=1, le=100),
) -> SecurityAlertsResponse:
    """Retrieve active security anomalies such as repeated Identity Mismatch violations."""
    alerts = await use_case.execute(
        window_minutes=window_minutes,
        threshold=threshold,
    )
    items = [
        SecurityAlertItemResponse(
            alert_id=a.alert_id,
            severity=a.severity,
            anomaly_type=a.anomaly_type,
            description=a.description,
            actor_id=a.actor_id,
            client_ip=a.client_ip,
            event_count=a.event_count,
            first_seen_at=a.first_seen_at,
            last_seen_at=a.last_seen_at,
        )
        for a in alerts
    ]
    return SecurityAlertsResponse(
        alerts=items,
        total_active=len(items),
    )
