from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ArticleORM(Base):
    
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    
    
    title = Column(String(255), nullable=False)
    
   
    content = Column(Text, nullable=False, name="text")
    
    source = Column(Text, nullable=False)
    
   
    link = Column(Text, unique=True, nullable=False, index=True)
    
   
    pub_date = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.now)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Добавляем UNIQUE constraint если его ещё нет
    from sqlalchemy import text
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        with engine.connect() as conn:
            # Пытаемся добавить constraint
            conn.execute(text("ALTER TABLE articles ADD CONSTRAINT articles_link_unique UNIQUE (link)"))
            conn.commit()
            logger.info("✅ UNIQUE constraint added to articles.link")
    except Exception as e:
        # Constraint уже существует или другая ошибка
        if "already exists" in str(e) or "duplicate key" in str(e):
            logger.info("ℹ️  UNIQUE constraint already exists on articles.link")
        else:
            logger.warning(f"⚠️  Note: {e}")
