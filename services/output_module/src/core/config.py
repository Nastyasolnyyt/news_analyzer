import os
from dotenv import load_dotenv

class Settings:
    def __init__(self) -> None:
        load_dotenv()

        # --- DATABASE SETTINGS ---
        # Приоритет для облачной базы (Render использует DATABASE_URL или POSTGRES_DB_URL)
        self.DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_DB_URL")

        # Если полной строки нет, пытаемся собрать из кирпичиков
        if not self.DATABASE_URL:
            # Только в этом случае эти переменные становятся обязательными
            pg_host = self._get_required_env("PG_HOST")
            pg_port = self._get_required_env("PG_PORT")
            pg_db = self._get_required_env("PG_DATABASE")
            pg_user = self._get_required_env("PG_USERNAME")
            pg_pass = self._get_required_env("PG_PASSWORD")
            self.DATABASE_URL = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
        
        # Важно для SQLAlchemy: Render часто дает ссылку 'postgres://', 
        # но современные версии библиотеки требуют 'postgresql://'
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)

        # --- REDIS SETTINGS ---
        # Для Redis добавим значения по умолчанию, чтобы не падать, если их нет
        self.REDIS_HOST = os.getenv("REDIS_HOST", "redis")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB_INDEX = int(os.getenv("REDIS_DB_INDEX", "0"))
        self.REDIS_USERNAME = os.getenv("REDIS_USERNAME", "default")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "password")

        # --- APP SETTINGS ---
        self.APP_PORT = int(os.getenv("APP_PORT", "8000"))
        self.APP_API_KEY = self._get_required_env("APP_API_KEY")

        # --- JWT SETTINGS ---
        self.JWT_SECRET_KEY = self._get_required_env("JWT_SECRET_KEY")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

        # --- SUPER ADMIN SETTINGS ---
        self.SUPERADMIN_INIT_TOKEN = self._get_required_env("SUPERADMIN_INIT_TOKEN")

    def _get_required_env(self, name: str) -> str:
        """Метод для получения обязательных переменных, без которых сервис не запустится"""
        value = os.getenv(name)
        if value is None:
            # Если мы здесь, значит ни DATABASE_URL, ни эта переменная не найдены
            raise EnvironmentError(f"Required environment variable '{name}' not set.")
        return value

# Создаем экземпляр настроек
env_settings = Settings()
