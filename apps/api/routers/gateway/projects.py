from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.routers.gateway.access_helpers import ensure_project_access
from core.security.deps import get_current_user_context, require_role_tier
from core.security.roles import RoleTier, UserContext
from modules.gateway.dtos.gateway_dtos import (
    ProjectCreateRequest,
    ProjectResponse,
)
from modules.gateway.use_cases import (
    CheckProjectMembershipUseCase,
    CreateProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    ProjectNotFoundError,
)

router = APIRouter()


@router.get(
    "/projects",
    response_model=list[ProjectResponse],
    summary="List registered projects accessible to the current user",
)
@inject
async def list_projects(
    use_case: FromDishka[ListProjectsUseCase],
    user_ctx: Annotated[UserContext, Depends(get_current_user_context)],
) -> list[ProjectResponse]:
    """Retrieve all projects (Admin) or assigned projects (Developer / Other)."""
    projects = await use_case.execute(
        user_id=user_ctx.user_id, is_admin=user_ctx.is_admin
    )
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
    membership_uc: FromDishka[CheckProjectMembershipUseCase],
    user_ctx: Annotated[UserContext, Depends(get_current_user_context)],
) -> ProjectResponse:
    """Retrieve single project by ID after verifying membership."""
    try:
        p = await use_case.execute(project_id)
        await ensure_project_access(project_id, user_ctx, membership_uc)
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
    summary="Create a new business project (Admin only)",
)
@inject
async def create_project(
    req: ProjectCreateRequest,
    use_case: FromDishka[CreateProjectUseCase],
    _: Annotated[UserContext, Depends(require_role_tier(RoleTier.ADMIN))],
) -> ProjectResponse:
    """Create a new business project."""
    project = await use_case.execute(
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
