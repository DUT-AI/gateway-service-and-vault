from core.exceptions.base import ForbiddenError


class ScopePermissionDeniedError(ForbiddenError):
    def __init__(
        self, message: str = "Permission denied for requested secret scope or key"
    ) -> None:
        super().__init__(message=message)
