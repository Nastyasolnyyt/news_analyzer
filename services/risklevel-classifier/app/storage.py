from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from .config import settings

Base = declarative_base()

class Risk(Base):
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True)
    article_id = Column(
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    risk_type = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

def save_risk_result(article_id: int, result):
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
    finally:
        db.close()