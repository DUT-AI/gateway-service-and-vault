from modules.gateway.domain.entities import ProjectMemberEntity
from modules.gateway.domain.interfaces import (
    IProjectMemberRepository,
    IProjectRepository,
)
from modules.gateway.use_cases.exceptions import ProjectNotFoundError


class AddProjectMemberUseCase:
    """Assigns one or more SSO users as members of a project in a single transaction."""

    def __init__(
        self,
        project_repo: IProjectRepository,
        member_repo: IProjectMemberRepository,
    ) -> None:
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def execute(
        self, project_id: str, user_ids: list[int], added_by: int
    ) -> list[ProjectMemberEntity]:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project '{project_id}' not found")
        results: list[ProjectMemberEntity] = []
        for uid in dict.fromkeys(user_ids):
            if uid >= 1:
                member = await self.member_repo.add_member(
                    project_id=project_id,
                    user_id=uid,
                    added_by=added_by,
                )
                results.append(member)
        return results


class RemoveProjectMemberUseCase:
    """Removes an SSO user's membership from a project."""

    def __init__(
        self,
        project_repo: IProjectRepository,
        member_repo: IProjectMemberRepository,
    ) -> None:
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def execute(self, project_id: str, user_id: int) -> bool:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project '{project_id}' not found")
        return await self.member_repo.remove_member(
            project_id=project_id,
            user_id=user_id,
        )


class ListProjectMembersUseCase:
    """Lists all SSO user memberships for a project."""

    def __init__(
        self,
        project_repo: IProjectRepository,
        member_repo: IProjectMemberRepository,
    ) -> None:
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def execute(self, project_id: str) -> list[ProjectMemberEntity]:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project '{project_id}' not found")
        return await self.member_repo.list_members(project_id)


class CheckProjectMembershipUseCase:
    """Checks whether an SSO user is a member of the specified project."""

    def __init__(self, member_repo: IProjectMemberRepository) -> None:
        self.member_repo = member_repo

    async def execute(self, project_id: str, user_id: int) -> bool:
        return await self.member_repo.is_member(project_id=project_id, user_id=user_id)
