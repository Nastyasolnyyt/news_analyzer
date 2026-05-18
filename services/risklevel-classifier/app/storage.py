"""
risklevel-classifier/app/storage.py
Сохранение уровней риска в PostgreSQL
"""
import logging
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

# Settings
class Settings(BaseSettings):
    database_url: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Models
Base = declarative_base()

class Risk(Base):
    """Модель таблицы risks"""
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), unique=True)
    
    # ✅ УРОВЕНЬ РИСКА (от risklevel-classifier)
    risk_level = Column(String)         # high / medium / low
    risk_confidence = Column(Float)     # 0..1 - уверенность УРОВНЯ
    
    # ❓ ТИП РИСКА (от risk-classifier) - может быть заполнено позже
    risk_type = Column(String)          # политический / экономический / социальный
    risk_type_confidence = Column(Float) # 0..1 - уверенность ТИПА
    
    created_at = Column(DateTime, server_default=func.now())

# Database
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Создаёт таблицы если их нет"""
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database инициализирована")


def save_risk_result(article_id: int, risk_level: str, confidence: float):
    """
    Сохраняет уровень риска для статьи
    
    Args:
        article_id: ID статьи
        risk_level: Уровень риска (high/medium/low)
        confidence: Уверенность (0..1)
    """
    db = SessionLocal()
    try:
        # UPSERT - если статья уже есть, обновляем; если нет, создаём
        stmt = insert(Risk).values(
            article_id=article_id,
            risk_level=risk_level,
            risk_confidence=confidence
        ).on_conflict_do_update(
            index_elements=['article_id'],
            set_={
                "risk_level": risk_level,
                "risk_confidence": confidence
            }
        )
        
        db.execute(stmt)
        db.commit()
        logger.debug(f"✅ Article {article_id}: {risk_level} ({confidence:.2f})")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Ошибка при сохранении риска для {article_id}: {e}")
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
