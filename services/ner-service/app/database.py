# services/ner-service/app/database.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

# Таблица именованных сущностей (соответствует реальной БД)
class NamedEntity(Base):
    __tablename__ = "named_entities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)  # unique=True убран — констрейнта нет в БД
    entity_type = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now())

# Таблица связи статья ↔ сущность (соответствует реальной БД)
class PostEntity(Base):
    __tablename__ = "post_entities"
    
    # ✅ НЕТ id — составной первичный ключ, как в реальной БД
    # ✅ Убраны ForeignKey — таблицы уже существуют, SQLAlchemy не нужно их создавать
    post_id = Column(Integer, nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)

# Подключение к БД
def get_engine(database_url: str):
    return create_engine(database_url, pool_pre_ping=True)

def get_session(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)