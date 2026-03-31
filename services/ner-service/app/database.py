# services/ner-service/app/database.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import insert

Base = declarative_base()

# Таблица именованных сущностей
class NamedEntity(Base):
    __tablename__ = "named_entities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)  # Уникальное имя сущности
    entity_type = Column(String, nullable=False)  # ORG, PER, LOC, MISC
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

# Таблица связи статья ↔ сущность
class PostEntity(Base):
    __tablename__ = "post_entities"
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_id = Column(Integer, ForeignKey("named_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Уникальная пара: одна сущность в статье только один раз
    __table_args__ = (
        UniqueConstraint('post_id', 'entity_id', name='uq_post_entity'),
    )

# Подключение к БД
def get_engine(database_url: str):
    return create_engine(database_url, pool_pre_ping=True)

def get_session(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)