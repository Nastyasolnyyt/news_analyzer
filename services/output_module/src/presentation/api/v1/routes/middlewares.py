from fastapi import Header
from fastapi.security import HTTPBearer
from src.application.errors.base_http_errors import UnauthorizedException
from src.core.config import Settings


config = Settings()
security = HTTPBearer()


def verify_api_key(x_auth_token: str = Header(...)) -> None:
    if x_auth_token != config.APP_API_KEY:
        raise UnauthorizedException()


def verify_superadmin_init_token(x_auth_token: str = Header(..., alias="X-Auth-Token")) -> None:
    """Проверяет токен для инициализации супер-админа."""
    if x_auth_token != config.SUPERADMIN_INIT_TOKEN:
        raise UnauthorizedException(message="Invalid superadmin init token")
