from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.core.config import env_settings

# Используем готовую строку подключения из нашего нового конфига
# Она уже содержит в себе логин, пароль, хост и название базы
SQLALCHEMY_DATABASE_URL = env_settings.DATABASE_URL

# Создаем движок. 
# pool_pre_ping=True — критически важно для облачных БД (Render/Heroku), 
# так как они обрывают неактивные соединения. Эта опция проверяет живое ли оно.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Настройка фабрики сессий
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Базовый класс для моделей
Base = declarative_base()

def get_db():
    """Хелпер для FastAPI зависимостей (Depends)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
