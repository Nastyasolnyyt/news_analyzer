from src.application.errors.base_http_errors import (
    EntityAlreadyExistException,
    EntityNotFoundException,
    UnauthorizedException,
)


class UserNotFoundException(EntityNotFoundException):
    def __init__(self, user_id: int | None = None):
        super().__init__(entity="User", entity_id=user_id)


class UserAlreadyExistsException(EntityAlreadyExistException):
    def __init__(self, login: str):
        super().__init__(entity="User", details={"login": login})


class InvalidCredentialsException(UnauthorizedException):
    def __init__(self):
        super().__init__(
            message="Invalid login or password", details={"error_code": "invalid_credentials"}
        )
