from core.exceptions.base import EntityNotFoundError, ForbiddenError


class ClientNotFoundError(EntityNotFoundError):
    def __init__(self, message: str = "Client not found") -> None:
        super().__init__(message=message)


class ProjectNotFoundError(EntityNotFoundError):
    def __init__(self, message: str = "Project not found") -> None:
        super().__init__(message=message)


class IdentityMismatchError(ForbiddenError):
    def __init__(
        self,
        message: str = "Identity mismatch: Virtual key is not bound to this client certificate or project",
    ) -> None:
        super().__init__(message=message)
