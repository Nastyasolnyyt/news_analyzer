# services/ner-service/app/database.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

# Таблица именованных сущностей
class NamedEntity(Base):
    __tablename__ = "named_entities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now())

# Таблица связи статья ↔ сущность (составной первичный ключ!)
class PostEntity(Base):
    __tablename__ = "post_entities"
    
    # ✅ ОБЯЗАТЕЛЬНО: primary_key=True для составного ключа
    post_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("named_entities.id", ondelete="CASCADE"), primary_key=True, index=True)