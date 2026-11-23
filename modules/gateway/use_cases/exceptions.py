from core.exceptions.base import ConflictError, EntityNotFoundError, ForbiddenError


class ClientNotFoundError(EntityNotFoundError):
    def __init__(self, message: str = "Client not found") -> None:
        super().__init__(message=message)


class ProjectNotFoundError(EntityNotFoundError):
    def __init__(self, message: str = "Project not found") -> None:
        super().__init__(message=message)


class ServiceNotFoundError(EntityNotFoundError):
    def __init__(self, message: str = "Upstream service not found") -> None:
        super().__init__(message=message)


class ServiceAlreadyBoundError(ConflictError):
    def __init__(
        self, message: str = "Upstream service is already bound to this project"
    ) -> None:
        super().__init__(message=message)


class ServiceNotBoundError(EntityNotFoundError):
    def __init__(
        self, message: str = "Upstream service is not bound to this project"
    ) -> None:
        super().__init__(message=message)


class ServiceNotPermittedError(ForbiddenError):
    def __init__(
        self,
        message: str = "Target upstream service is not permitted for this project",
    ) -> None:
        super().__init__(message=message)


class IdentityMismatchError(ForbiddenError):
    def __init__(
        self,
        message: str = "Identity mismatch: Virtual key is not bound to this client certificate or project",
    ) -> None:
        super().__init__(message=message)
