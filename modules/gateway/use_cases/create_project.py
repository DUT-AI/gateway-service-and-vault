from modules.gateway.domain.entities import ProjectEntity
from modules.gateway.domain.interfaces import IProjectRepository


class CreateProjectUseCase:
    """Use case to create a business project."""

    def __init__(self, project_repo: IProjectRepository) -> None:
        self.project_repo = project_repo

    async def execute(
        self,
        name: str,
        slug: str,
        description: str | None = None,
    ) -> ProjectEntity:
        return await self.project_repo.create(
            name=name,
            slug=slug,
            description=description,
        )
