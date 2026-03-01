from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt
from src.application.enums import UserRole
from src.application.errors.user import InvalidCredentialsException
from src.application.schemas.user import LoginRequestDTO, RefreshTokenRequestDTO, TokenResponseDTO
from src.core.config import env_settings
from src.infrastructure.postgres.repositories.user import UserDBGateWay


class AuthService:
    def __init__(self, user_gateway: UserDBGateWay):
        self.user_gateway = user_gateway
        self.secret_key = env_settings.JWT_SECRET_KEY
        self.algorithm = env_settings.JWT_ALGORITHM
        self.access_token_expire_minutes = env_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = env_settings.REFRESH_TOKEN_EXPIRE_DAYS

    @staticmethod
    def hash_password(password: str) -> str:
        """Хэширует пароль с помощью bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Проверяет пароль против хэша."""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def create_access_token(self, user_id: int, role: UserRole) -> str:
        """Создает access токен."""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": str(user_id),
            "role": role.value,
            "type": "access",
            "exp": expire,
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: int) -> str:
        """Создает refresh токен."""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {"sub": str(user_id), "type": "refresh", "exp": expire}
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str, token_type: str = "access") -> dict:
        """Декодирует и валидирует токен."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                raise InvalidCredentialsException()
            return payload
        except JWTError:
            raise InvalidCredentialsException()

    async def login(self, login_data: LoginRequestDTO) -> TokenResponseDTO:
        """Аутентифицирует пользователя и возвращает токены."""
        user_data = await self.user_gateway.get_user_with_password_by_login(login_data.login)
        if user_data is None:
            raise InvalidCredentialsException()

        user, password_hash = user_data

        if not self.verify_password(login_data.password, password_hash):
            raise InvalidCredentialsException()

        access_token = self.create_access_token(user.id, user.role)
        refresh_token = self.create_refresh_token(user.id)

        return TokenResponseDTO(access_token=access_token, refresh_token=refresh_token)

    async def refresh_token(self, refresh_data: RefreshTokenRequestDTO) -> TokenResponseDTO:
        """Обновляет access токен используя refresh токен."""
        payload = self.decode_token(refresh_data.refresh_token, token_type="refresh")
        user_id = int(payload["sub"])

        user = await self.user_gateway.get_user_by_id(user_id)
        access_token = self.create_access_token(user.id, user.role)
        refresh_token = self.create_refresh_token(user.id)

        return TokenResponseDTO(access_token=access_token, refresh_token=refresh_token)
