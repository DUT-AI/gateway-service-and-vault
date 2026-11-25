from datetime import UTC, datetime

from modules.gateway.domain.entities import RegisteredClientEntity
from modules.gateway.domain.interfaces import (
    IProjectMemberRepository,
    IRegisteredClientRepository,
)


class ListProjectAvailableClientsUseCase:
    """List active mTLS clients eligible to be bound to a project's Virtual Keys."""

    def __init__(
        self,
        client_repo: IRegisteredClientRepository,
        member_repo: IProjectMemberRepository,
    ) -> None:
        self.client_repo = client_repo
        self.member_repo = member_repo

    async def execute(
        self,
        project_id: str,
        caller_owner_id: str | None = None,
        is_admin: bool = False,
    ) -> list[RegisteredClientEntity]:
        if is_admin:
            clients = await self.client_repo.list_all()
        else:
            members = await self.member_repo.list_members(project_id)
            owner_ids = {str(m.user_id) for m in members}
            if caller_owner_id:
                owner_ids.add(caller_owner_id)
            clients = await self.client_repo.list_by_owner_ids(list(owner_ids))

        now = datetime.now(UTC)
        active: list[RegisteredClientEntity] = []
        for c in clients:
            if c.is_revoked:
                continue
            expires = c.expires_at
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=UTC)
            if expires <= now:
                continue
            active.append(c)
        return active
