from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Path, status

from core.security.deps import require_role_tier
from core.security.roles import RoleTier, UserContext
from modules.gateway.dtos.gateway_dtos import (
    ProjectMemberCreateRequest,
    ProjectMemberResponse,
)
from modules.gateway.use_cases import (
    AddProjectMemberUseCase,
    ListProjectMembersUseCase,
    ProjectNotFoundError,
    RemoveProjectMemberUseCase,
)

router = APIRouter()


@router.get(
    "/projects/{project_id}/members",
    summary="List all members assigned to a project (Admin only)",
)
@inject
async def list_project_members(
    project_id: str,
    use_case: FromDishka[ListProjectMembersUseCase],
    _: Annotated[UserContext, Depends(require_role_tier(RoleTier.ADMIN))],
) -> list[ProjectMemberResponse]:
    """Retrieve all SSO user memberships for a project."""
    try:
        members = await use_case.execute(project_id)
        return [
            ProjectMemberResponse(
                id=m.id,
                project_id=m.project_id,
                user_id=m.user_id,
                added_by=m.added_by,
                created_at=m.created_at,
            )
            for m in members
        ]
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.post(
    "/projects/{project_id}/members",
    response_model=list[ProjectMemberResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Assign one or more SSO users to a project (Admin only)",
)
@inject
async def add_project_member(
    project_id: str,
    req: ProjectMemberCreateRequest,
    use_case: FromDishka[AddProjectMemberUseCase],
    admin_ctx: Annotated[UserContext, Depends(require_role_tier(RoleTier.ADMIN))],
) -> list[ProjectMemberResponse]:
    """Assign multiple SSO users as members of the project in a single request."""
    try:
        members = await use_case.execute(
            project_id=project_id,
            user_ids=req.user_ids,
            added_by=admin_ctx.user_id,
        )
        return [
            ProjectMemberResponse(
                id=m.id,
                project_id=m.project_id,
                user_id=m.user_id,
                added_by=m.added_by,
                created_at=m.created_at,
            )
            for m in members
        ]
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.delete(
    "/projects/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an SSO user from a project (Admin only)",
)
@inject
async def remove_project_member(
    project_id: str,
    use_case: FromDishka[RemoveProjectMemberUseCase],
    _: Annotated[UserContext, Depends(require_role_tier(RoleTier.ADMIN))],
    user_id: int = Path(..., ge=1),
) -> None:
    """Remove an SSO user's membership from the project."""
    try:
        removed = await use_case.execute(project_id=project_id, user_id=user_id)
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} is not a member of project '{project_id}'",
            )
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
