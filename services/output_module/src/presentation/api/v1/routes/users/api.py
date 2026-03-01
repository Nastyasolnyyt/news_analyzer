from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends
from src.application.enums import UserRole
from src.application.errors.base_http_errors import ForbiddenException
from src.application.schemas.user import (
    UserCreateDTO,
    UserDTO,
    UserFilterDTO,
    UserListResponseDTO,
    UserUpdateDTO,
)
from src.presentation.api.v1.routes.auth_dependencies import (
    check_user_role,
    get_current_user,
)
from src.services.user_service import UserService


ROUTER = APIRouter(prefix="/users", route_class=DishkaRoute, tags=["Users"])


@ROUTER.post("", response_model=UserDTO, summary="Создать пользователя")
async def create_user(
    user_service: FromDishka[UserService],
    user_data: UserCreateDTO,
    user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    """Создание пользователя. Только для супер-админа."""
    check_user_role(user, UserRole.SUPERADMIN)
    return await user_service.create_user(user_data)


@ROUTER.get("", response_model=UserListResponseDTO, summary="Список пользователей")
async def get_users(
    user_service: FromDishka[UserService],
    filters: UserFilterDTO = Depends(),
) -> UserListResponseDTO:
    """Получение списка пользователей с фильтрацией и пагинацией."""
    return await user_service.get_users(filters)


@ROUTER.get("/{user_id}", response_model=UserDTO, summary="Получить пользователя")
async def get_user(
    user_service: FromDishka[UserService],
    user_id: int,
    user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    """Получение информации о пользователе по ID."""
    # Пользователь может видеть только свою информацию, админы - всех
    if user.role not in [UserRole.SUPERADMIN, UserRole.ADMIN] and user.id != user_id:
        raise ForbiddenException(message="You can only view your own profile")
    return await user_service.get_user(user_id)


@ROUTER.patch("/{user_id}", response_model=UserDTO, summary="Обновить пользователя")
async def update_user(
    user_service: FromDishka[UserService],
    user_id: int,
    user_data: UserUpdateDTO,
    user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    """Обновление информации о пользователе."""
    # Пользователь может обновлять только свою информацию, админы - всех
    if user.role not in [UserRole.SUPERADMIN, UserRole.ADMIN] and user.id != user_id:
        raise ForbiddenException(message="You can only update your own profile")
    # Пользователь не может менять свою роль
    if user.role not in [UserRole.SUPERADMIN, UserRole.ADMIN] and user_data.role is not None:
        raise ForbiddenException(message="You cannot change your role")
    return await user_service.update_user(user_id, user_data)
