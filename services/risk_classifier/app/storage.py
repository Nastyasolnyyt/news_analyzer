from sqlalchemy import create_engine, Column, Integer, String, Float, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert
from .config import settings

Base = declarative_base()

class Risk(Base):
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, unique=True, index=True)
    risk_type = Column(String)
    confidence = Column(Float)

    __table_args__ = (UniqueConstraint('article_id', name='unique_article_risk'),)

engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def save_risk_result(article_id: int, result: RiskResult):
    with SessionLocal() as db:
        try:
            stmt = insert(Risk).values(
                article_id=article_id,
                risk_type=result.risk_type,
                confidence=result.confidence
            )
            # Если запись уже есть — обновляем её
            stmt = stmt.on_conflict_do_update(
                constraint="unique_article_risk",
                set_={
                    "risk_type": result.risk_type,
                    "confidence": result.confidence
                }
            )
            db.execute(stmt)
            db.commit()
        except Exception:
            db.rollback()
            raise

def init_db():
    Base.metadata.create_all(bind=engine)