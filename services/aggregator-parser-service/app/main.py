# main.py
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime, select
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert # Нужно для UPSERT
import os

from .parsers import parse_rss
from .kafka_producer import send_article_to_kafka 
from .models import Article
from typing import List

# --- Настройка Базы Данных ---
DATABASE_URL = os.getenv("DATABASE_URL")
# Убираем sslmode если работаем в локальном докере, или оставляем для облака
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class ArticleORM(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    text = Column(String)
    link = Column(String, unique=True) 
    source = Column(String)
    pub_date = Column(DateTime)

app = FastAPI(title="Aggregator Parser Service")

@app.post("/parse", response_model=List[Article])
async def parse_aggregator(urls: List[str]):
    all_articles = []
    db = SessionLocal()
    try:
        for url in urls:
            articles = parse_rss(url.strip())
            for art_data in articles:
                # Используем UPSERT логику для PostgreSQL
                stmt = insert(ArticleORM).values(
                    title=art_data.title,
                    text=art_data.text,
                    link=art_data.link,
                    source=art_data.source,
                    pub_date=art_data.pub_date
                )
                
                # Если ссылка (link) уже есть — ничего не делаем, но нам нужен ID
                stmt = stmt.on_conflict_do_nothing(index_elements=['link'])
                result = db.execute(stmt)
                db.commit()

                # Находим реальный ID (либо только что созданный, либо существующий)
                existing_article = db.query(ArticleORM).filter(ArticleORM.link == art_data.link).first()
                
                if existing_article:
                    art_data.id = existing_article.id # ТЕПЕРЬ ТУТ ВСЕГДА РЕАЛЬНЫЙ ID
                    
                    print(f"DEBUG: Статья ID {art_data.id} готова к отправке")
                    await send_article_to_kafka(art_data)
                    all_articles.append(art_data)
        
        return all_articles
    except Exception as e:
        print(f"DEBUG: ОШИБКА: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()