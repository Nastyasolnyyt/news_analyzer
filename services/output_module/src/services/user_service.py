from src.application.schemas.user import (
    UserCreateDTO,
    UserDTO,
    UserFilterDTO,
    UserListResponseDTO,
    UserUpdateDTO,
)
from src.infrastructure.postgres.repositories.user import UserDBGateWay
from src.services.auth import AuthService


class UserService:
    def __init__(self, user_gateway: UserDBGateWay, auth_service: AuthService):
        self.user_gateway = user_gateway
        self.auth_service = auth_service

    async def create_user(self, user_data: UserCreateDTO) -> UserDTO:
        password_hash = self.auth_service.hash_password(user_data.password)
        return await self.user_gateway.create_user(
            login=user_data.login,
            username=user_data.username,
            password_hash=password_hash,
            name=user_data.name,
            role=user_data.role,
        )
    async def get_user(self, user_id: int) -> UserDTO:
        """Получает пользователя по ID."""
        return await self.user_gateway.get_user_by_id(user_id)

    async def get_users(self, filters: UserFilterDTO) -> UserListResponseDTO:
        """Получает список пользователей с фильтрацией и пагинацией."""
        users, total = await self.user_gateway.get_users_with_filters(filters)
        return UserListResponseDTO(
            items=users, total=total, page=filters.page, page_size=filters.page_size
        )

    async def update_user(self, user_id: int, user_data: UserUpdateDTO) -> UserDTO:
        """Обновляет пользователя."""
        password_hash = None
        if user_data.password is not None:
            password_hash = self.auth_service.hash_password(user_data.password)

        return await self.user_gateway.update_user(
            user_id=user_id,
            name=user_data.name,
            role=user_data.role,
            password_hash=password_hash,
        )
