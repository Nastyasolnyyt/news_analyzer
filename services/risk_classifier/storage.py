from sqlalchemy import create_engine, Column, Integer, String, Float, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert
from .config import settings # Импортируем из вашего конфига

Base = declarative_base()

class Risk(Base):
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True, index=True)
    # Важно: article_id должен быть уникальным, чтобы работал UPSERT
    article_id = Column(Integer, unique=True, index=True) 
    risk_type = Column(String)
    confidence = Column(Float)

    # Альтернативно можно задать именованное ограничение:
    __table_args__ = (UniqueConstraint('article_id', name='unique_article_risk'),)

engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def save_risk_result(article_id: int, result):
    """
    Сохраняет результат классификации. 
    Если запись для этого article_id уже есть — обновляет её.
    """
    with SessionLocal() as db: # Используем контекстный менеджер для авто-закрытия
        try:
            # Подготовка UPSERT (PostgreSQL specific)
            stmt = insert(Risk).values(
                article_id=article_id,
                risk_type=result.risk_type,
                confidence=result.confidence
            )
            
            # Определяем, что делать при конфликте
            stmt = stmt.on_conflict_do_update(
                constraint="unique_article_risk", # Имя констрейнта в БД
                set_={
                    "risk_type": result.risk_type,
                    "confidence": result.confidence
                }
            )
            
            db.execute(stmt)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e