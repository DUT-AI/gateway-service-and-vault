from fastapi import HTTPException, status

from core.security.roles import UserContext
from modules.gateway.use_cases import CheckProjectMembershipUseCase


async def ensure_project_access(
    project_id: str,
    user_ctx: UserContext,
    membership_uc: CheckProjectMembershipUseCase,
) -> None:
    """Verify that non-admin users belong to the target project via Project Membership."""
    if user_ctx.is_admin:
        return
    is_member = await membership_uc.execute(
        project_id=project_id, user_id=user_ctx.user_id
    )
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không thuộc dự án này hoặc chưa được cấp quyền truy cập dự án",
        )
