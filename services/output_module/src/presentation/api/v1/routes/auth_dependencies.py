from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from src.application.enums import UserRole
from src.application.errors.base_http_errors import ForbiddenException, UnauthorizedException
from src.application.errors.user import UserNotFoundException
from src.application.schemas.user import UserDTO
from src.services.auth import AuthService
from src.services.user_service import UserService


bearer_scheme = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UserDTO:
    """Получает текущего пользователя из JWT токена в заголовке Authorization."""
    token = credentials.credentials
    if not token:
        logger.error("Отсутствует токен авторизации")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid",
        )

    try:
        # Получаем контейнер Dishka из request state
        from dishka.integrations.fastapi import get_container

        container = get_container(request)
        auth_service = await container.get(AuthService)
        user_service = await container.get(UserService)

        payload = auth_service.decode_token(token, token_type="access")
        user_id = int(payload["sub"])
        logger.info("Токен верифицирован", {"user_id": user_id})

        user = await user_service.get_user(user_id)
        logger.info(
            "Пользователь получен из БД для аутентификации",
            {"user_id": user.id, "login": user.login},
        )
        return user
    except (HTTPException, UserNotFoundException, UnauthorizedException) as e:
        logger.error("Ошибка аутентификации", {"error": str(e)})
        raise e
    except Exception as e:
        logger.error("Внутренняя ошибка аутентификации", {"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal authentication error: {str(e)}",
        )


def check_user_role(user: UserDTO, *allowed_roles: UserRole) -> None:
    """Проверяет, имеет ли пользователь одну из разрешенных ролей."""
    if user.role not in allowed_roles:
        raise ForbiddenException(
            message=f"Access denied. Required roles: {', '.join([r.value for r in allowed_roles])}"
        )
