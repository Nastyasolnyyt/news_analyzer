import os

from dotenv import load_dotenv


class Settings:
    def __init__(self) -> None:
        load_dotenv()
        # Postgres Settings
        self.PG_HOST = self._get_required_env("PG_HOST")
        self.PG_PORT = int(self._get_required_env("PG_PORT"))
        self.PG_DATABASE = self._get_required_env("PG_DATABASE")
        self.PG_USERNAME = self._get_required_env("PG_USERNAME")
        self.PG_PASSWORD = self._get_required_env("PG_PASSWORD")

        # Redis Settings
        self.REDIS_HOST = self._get_required_env("REDIS_HOST")
        self.REDIS_PORT = int(self._get_required_env("REDIS_PORT"))
        self.REDIS_DB_INDEX = int(self._get_required_env("REDIS_DB_INDEX"))
        self.REDIS_USERNAME = self._get_required_env("REDIS_USERNAME")
        self.REDIS_PASSWORD = self._get_required_env("REDIS_PASSWORD")

        # APP Settings
        self.APP_PORT = int(self._get_required_env("APP_PORT"))
        self.APP_API_KEY = self._get_required_env("APP_API_KEY")

        # JWT Settings
        self.JWT_SECRET_KEY = self._get_required_env("JWT_SECRET_KEY")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

        # Super Admin Settings
        self.SUPERADMIN_INIT_TOKEN = self._get_required_env("SUPERADMIN_INIT_TOKEN")

    def _get_required_env(self, name: str) -> str:
        value = os.getenv(name)
        if value is None:
            raise EnvironmentError(f"Required environment variable '{name}' not set.")
        return value


env_settings = Settings()
