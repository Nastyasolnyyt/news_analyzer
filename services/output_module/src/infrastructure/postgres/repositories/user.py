from typing import Optional, List, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.enums import UserRole
from src.application.errors.user import UserAlreadyExistsException, UserNotFoundException
from src.application.schemas.user import UserDTO, UserFilterDTO
from src.infrastructure.postgres.models.user import User


class UserDBGateWay:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> UserDTO:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user is None:
            raise UserNotFoundException(user_id=user_id)
        return UserDTO.model_validate(user, from_attributes=True)

    async def get_user_by_login(self, login: str) -> Optional[UserDTO]:
        result = await self.session.execute(select(User).where(User.login == login))
        user = result.scalars().first()
        if user is None:
            return None
        return UserDTO.model_validate(user, from_attributes=True)

    async def get_user_with_password_by_login(self, login: str) -> Optional[Tuple[UserDTO, str]]:
        """Возвращает UserDTO и password_hash для проверки пароля."""
        result = await self.session.execute(select(User).where(User.login == login))
        user = result.scalars().first()
        if user is None:
            return None

        user_dto = UserDTO.model_validate(user, from_attributes=True)
        return user_dto, user.password_hash

    async def create_user(
        self, login: str, password_hash: str, name: str, role: UserRole
    ) -> UserDTO:
        # Проверяем существование
        existing_user = await self.get_user_by_login(login)
        if existing_user is not None:
            raise UserAlreadyExistsException(login=login)

        new_user = User(
            login=login,
            password_hash=password_hash,
            name=name,
            role=role.value,
        )
        self.session.add(new_user)
        await self.session.flush()
        await self.session.refresh(new_user)
        return UserDTO.model_validate(new_user, from_attributes=True)

    async def update_user(
        self,
        user_id: int,
        login: Optional[str] = None,
        name: Optional[str] = None,
        role: Optional[UserRole] = None,
        password_hash: Optional[str] = None,
    ) -> UserDTO:
        user_result = await self.session.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user is None:
            raise UserNotFoundException(user_id=user_id)

        if login is not None:
            user.login = login
        if name is not None:
            user.name = name
        if role is not None:
            user.role = role.value
        if password_hash is not None:
            user.password_hash = password_hash

        await self.session.flush()
        await self.session.refresh(user)
        return UserDTO.model_validate(user, from_attributes=True)

    async def get_users_with_filters(self, filters: UserFilterDTO) -> Tuple[List[UserDTO], int]:
        query = select(User)

        # Фильтры
        if filters.role is not None:
            query = query.where(User.role == filters.role.value)
        if filters.login is not None:
            query = query.where(User.login.ilike(f"%{filters.login}%"))

        # Подсчет общего количества
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Пагинация
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size).order_by(User.id.desc())

        result = await self.session.execute(query)
        users = result.scalars().all()

        return [UserDTO.model_validate(u, from_attributes=True) for u in users], total