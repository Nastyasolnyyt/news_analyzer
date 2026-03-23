from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from .config import settings

Base = declarative_base()

class PostAnalysis(Base):
    __tablename__ = "articles_analysis"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, unique=True)
    # Поля, которые заполняет ЭТОТ сервис
    risk_level = Column(String, default='low')
    confidence = Column(Float, default=0.0)
    # Остальные поля просто объявляем, чтобы SQLAlchemy не ругался
    topic_id = Column(Integer, nullable=True)
    category = Column(String, nullable=True)
    emotion = Column(Float, default=0.0)
    tonality = Column(Float, default=0.0)
    relevance = Column(Float, default=0.0)

engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(bind=engine)

def save_risk_result(article_id: int, result):
    db = SessionLocal()
    try:
        # UPSERT: если запись для статьи уже есть (от другого сервиса), 
        # мы просто ОБНОВЛЯЕМ поля риска, не трогая категорию или тональность.
        stmt = insert(PostAnalysis).values(
            post_id=article_id,
            risk_level=result.risk_type,
            confidence=result.confidence
        ).on_conflict_do_update(
            index_elements=['post_id'],
            set_={
                "risk_level": result.risk_type,
                "confidence": result.confidence
            }
        )
        db.execute(stmt)
        db.commit()
    finally:
        db.close()