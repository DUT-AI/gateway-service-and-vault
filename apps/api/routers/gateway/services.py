from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.routers.gateway.access_helpers import ensure_project_access
from core.security.deps import get_current_user_context, require_role_tier
from core.security.roles import RoleTier, UserContext
from modules.gateway.dtos.gateway_dtos import (
    BindServiceToProjectRequest,
    ProjectAllowedServiceResponse,
    QuotaUsageResponse,
    UpdateServiceQuotaRequest,
    UpstreamServiceCreateRequest,
    UpstreamServiceResponse,
)
from modules.gateway.use_cases import (
    BindServiceToProjectUseCase,
    CheckProjectMembershipUseCase,
    CreateUpstreamServiceUseCase,
    GetProjectServiceUsageUseCase,
    ListProjectAllowedServicesUseCase,
    ListUpstreamServicesUseCase,
    ProjectNotFoundError,
    ServiceAlreadyBoundError,
    ServiceNotBoundError,
    ServiceNotFoundError,
    UnbindServiceFromProjectUseCase,
    UpdateProjectServiceQuotaUseCase,
)

router = APIRouter()


@router.get(
    "/services",
    response_model=list[UpstreamServiceResponse],
    summary="List all upstream backend services",
)
@inject
async def list_upstream_services(
    use_case: FromDishka[ListUpstreamServicesUseCase],
    _: Annotated[
        UserContext,
        Depends(require_role_tier(RoleTier.ADMIN, RoleTier.PROJECT_DEVELOPER)),
    ],
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
    _: Annotated[UserContext, Depends(require_role_tier(RoleTier.ADMIN))],
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


@router.get(
    "/projects/{project_id}/services",
    response_model=list[ProjectAllowedServiceResponse],
    summary="List all allowed upstream services and quota for a project",
)
@inject
async def list_project_allowed_services(
    project_id: str,
    use_case: FromDishka[ListProjectAllowedServicesUseCase],
    membership_uc: FromDishka[CheckProjectMembershipUseCase],
    user_ctx: Annotated[UserContext, Depends(get_current_user_context)],
) -> list[ProjectAllowedServiceResponse]:
    """Retrieve all upstream services bound to this project with their quota policies and usage."""
    try:
        await ensure_project_access(project_id, user_ctx, membership_uc)
        items = await use_case.execute(project_id)
        return [
            ProjectAllowedServiceResponse(
                service_id=item.service_id,
                service_name=item.service_name,
                service_slug=item.service_slug,
                base_url=item.base_url,
                auth_type=item.auth_type,
                is_service_active=item.is_service_active,
                rate_limit_rpm=item.rate_limit_rpm,
                quota_daily=item.quota_daily,
                is_quota_active=item.is_quota_active,
                usage_today=item.usage_today,
                usage_percentage=item.usage_percentage,
                bound_at=item.bound_at,
            )
            for item in items
        ]
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
    membership_uc: FromDishka[CheckProjectMembershipUseCase],
    user_ctx: Annotated[UserContext, Depends(get_current_user_context)],
) -> QuotaUsageResponse:
    """Retrieve today's request usage count and quota consumption percentage."""
    await ensure_project_access(project_id, user_ctx, membership_uc)
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
    _: Annotated[UserContext, Depends(require_role_tier(RoleTier.ADMIN))],
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
    _: Annotated[UserContext, Depends(require_role_tier(RoleTier.ADMIN))],
) -> ProjectAllowedServiceResponse:
    """Update rate limit RPM or daily quota for a project-service binding."""
    try:
        svc, quota = await use_case.execute(
            project_id=project_id,
            service_id=service_id,
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
    except (ServiceNotFoundError, ServiceNotBoundError) as e:
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
    _: Annotated[UserContext, Depends(require_role_tier(RoleTier.ADMIN))],
) -> None:
    """Revoke a project's access to an upstream service and delete its quota policy."""
    try:
        await use_case.execute(project_id, service_id)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceNotBoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
