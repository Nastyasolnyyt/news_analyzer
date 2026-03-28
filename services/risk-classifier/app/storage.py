"""
risk-classifier/app/storage.py
Сохранение типов риска в PostgreSQL
"""
import logging
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert
from .config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

class Risk(Base):
    """Модель таблицы risks"""
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, unique=True, index=True)
    risk_type = Column(String)          # политический / экономический / социальный
    confidence = Column(Float)          # уверенность типа риска

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Создаёт таблицы если их нет"""
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database инициализирована")

def save_risk_result(article_id: int, result):
    """
    Сохраняет тип риска для статьи (принимает объект result)
    """
    db = SessionLocal()
    try:
        stmt = insert(Risk).values(
            article_id=article_id,
            risk_type=result.risk_type,
            confidence=result.confidence
        ).on_conflict_do_update(
            index_elements=['article_id'],
            set_={
                "risk_type": result.risk_type,
                "confidence": result.confidence
            }
        )
        db.execute(stmt)
        db.commit()
        logger.debug(f"✅ Article {article_id}: {result.risk_type} ({result.confidence:.2f})")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Ошибка при сохранении риска для {article_id}: {e}")
        raise
    finally:
        db.close()

def save_risk_type(article_id: int, risk_type: str, confidence: float):
    """
    Сохраняет тип риска для статьи (принимает отдельные параметры)
    Args:
        article_id: ID статьи
        risk_type: Тип риска (политический/экономический/социальный)
        confidence: Уверенность (0..1)
    """
    db = SessionLocal()
    try:
        stmt = insert(Risk).values(
            article_id=article_id,
            risk_type=risk_type,
            confidence=confidence
        ).on_conflict_do_update(
            index_elements=['article_id'],
            set_={
                "risk_type": risk_type,
                "confidence": confidence
            }
        )
        db.execute(stmt)
        db.commit()
        logger.debug(f"✅ Article {article_id}: type={risk_type} ({confidence:.2f})")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Ошибка при сохранении типа риска для {article_id}: {e}")
        raise
    finally:
        db.close()