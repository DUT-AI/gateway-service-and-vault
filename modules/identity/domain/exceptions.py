from core.exceptions import ConflictError, EntityNotFoundError, UnauthorizedError


class UserNotFoundError(EntityNotFoundError):
    """Raised when user with given identifier or email is not found."""

    def __init__(self, user_identifier: str | int) -> None:
        super().__init__(
            message=f"User with identifier '{user_identifier}' not found",
            details={"user_identifier": user_identifier},
        )


class UserAlreadyExistsError(ConflictError):
    """Raised when attempting to create a user with an existing email."""

    def __init__(self, email: str) -> None:
        super().__init__(
            message=f"User with email '{email}' already exists",
            details={"email": email},
        )


class InvalidCredentialsError(UnauthorizedError):
    """Raised when email or password authentication fails."""

    def __init__(self) -> None:
        super().__init__(message="Invalid email or password")
