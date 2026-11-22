"""Domain exception hierarchy. Pure Python, decoupled from HTTP/transport."""


class DomainException(Exception):
    """Base exception for all business domain errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvariantViolationError(DomainException):
    """Raised when an internal aggregate invariant or contract is broken."""

    def __init__(
        self, message: str = "Domain invariant violation", details: dict | None = None
    ) -> None:
        super().__init__(message, details)


class BusinessRuleViolationError(DomainException):
    """Raised when a business policy or domain workflow rule is violated."""

    def __init__(
        self, message: str = "Business rule violation", details: dict | None = None
    ) -> None:
        super().__init__(message, details)


class EntityNotFoundError(DomainException):
    """Raised when a requested domain entity does not exist."""

    def __init__(
        self, message: str = "Entity not found", details: dict | None = None
    ) -> None:
        super().__init__(message, details)


class ConflictError(DomainException):
    """Raised when a unique constraint or concurrency conflict occurs."""

    def __init__(
        self, message: str = "Resource conflict", details: dict | None = None
    ) -> None:
        super().__init__(message, details)


class UnauthorizedError(DomainException):
    """Raised when credentials or token are missing or invalid."""

    def __init__(
        self, message: str = "Unauthorized", details: dict | None = None
    ) -> None:
        super().__init__(message, details)


class ForbiddenError(DomainException):
    """Raised when user lacks permission to perform the requested action."""

    def __init__(self, message: str = "Forbidden", details: dict | None = None) -> None:
        super().__init__(message, details)


class StorageError(DomainException):
    """Raised when an object storage operation fails."""

    def __init__(
        self, message: str = "Storage error", details: dict | None = None
    ) -> None:
        super().__init__(message, details)
