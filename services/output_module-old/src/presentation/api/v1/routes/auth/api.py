from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends
from src.application.enums import UserRole
from src.application.schemas.user import (
    LoginRequestDTO,
    RefreshTokenRequestDTO,
    TokenResponseDTO,
    UserCreateDTO,
    UserDTO,
)
from src.presentation.api.v1.routes.middlewares import verify_superadmin_init_token
from src.services.auth import AuthService
from src.services.user_service import UserService


ROUTER = APIRouter(prefix="/auth", route_class=DishkaRoute, tags=["Auth"])


@ROUTER.post("/login", response_model=TokenResponseDTO, summary="Вход в систему")
async def login(
    login_data: LoginRequestDTO,
    auth_service: FromDishka[AuthService],
) -> TokenResponseDTO:
    """Аутентификация пользователя. Возвращает access и refresh токены."""
    return await auth_service.login(login_data)


@ROUTER.post("/refresh", response_model=TokenResponseDTO, summary="Обновление токена")
async def refresh(
    refresh_data: RefreshTokenRequestDTO,
    auth_service: FromDishka[AuthService],
) -> TokenResponseDTO:
    """Обновляет access токен используя refresh токен."""
    return await auth_service.refresh_token(refresh_data)


@ROUTER.post(
    "/superadmin/init",
    response_model=UserDTO,
    summary="Инициализация супер-админа",
    dependencies=[Depends(verify_superadmin_init_token)],
)
async def init_superadmin(
    user_data: UserCreateDTO,
    user_service: FromDishka[UserService],
) -> UserDTO:
    """Создает супер-админа. Требует X-Auth-Token заголовок."""
    # Принудительно устанавливаем роль SUPERADMIN
    user_data.role = UserRole.SUPERADMIN
    return await user_service.create_user(user_data)
