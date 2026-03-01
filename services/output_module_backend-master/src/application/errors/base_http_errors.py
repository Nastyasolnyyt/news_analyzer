from typing import Any, Dict, Optional, Union

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(status_code=status_code, detail=self._build_detail())

    def _build_detail(self) -> Dict[str, Any]:
        return {
            "error": {"code": self.error_code, "message": self.message, "details": self.details}
        }


# 400 — валидационные ошибки
class ValidationErrorException(BaseAPIException):
    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["value"] = value

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="validation_error",
            message=message,
            details=error_details,
        )


# 401 — неавторизовано
class UnauthorizedException(BaseAPIException):
    def __init__(
        self,
        message: str = "Unauthorized",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="unauthorized",
            message=message,
            details=details or {},
        )


# 403 — нет прав
class ForbiddenException(BaseAPIException):
    def __init__(
        self,
        message: str = "Forbidden",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="forbidden",
            message=message,
            details=details or {},
        )


# 404 — не найдено
class EntityNotFoundException(BaseAPIException):
    def __init__(
        self,
        entity: str,
        entity_id: Optional[Union[int, str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if entity_id is not None:
            error_details["entity_id"] = entity_id
            error_details["entity_type"] = entity

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="not_found",
            message=f"{entity} is not found",
            details=error_details,
        )


# 409 — конфликт
class EntityAlreadyExistException(BaseAPIException):
    def __init__(
        self,
        entity: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        error_details["entity_type"] = entity

        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="already_exists",
            message=f"{entity} is already exist",
            details=error_details,
        )


class EntityConflictException(BaseAPIException):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="conflict",
            message=message,
            details=details or {},
        )


# 500 — внутренняя ошибка сервера
class InternalServerException(BaseAPIException):
    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="internal_error",
            message=message,
            details=details or {},
        )
