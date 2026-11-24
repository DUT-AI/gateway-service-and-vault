from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, status

from modules.gateway.dtos.gateway_dtos import (
    ProjectCreateRequest,
    ProjectResponse,
)
from modules.gateway.use_cases import (
    CreateProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    ProjectNotFoundError,
)

router = APIRouter()


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
    use_case: FromDishka[CreateProjectUseCase],
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
