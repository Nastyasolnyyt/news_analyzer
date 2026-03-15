from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from .parsers import parse_rss
from .kafka_producer import send_article_to_kafka 
from .models import Article
from typing import List

# --- Настройка Базы Данных ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require",
    },
    pool_pre_ping=True,  # Проверяет соединение перед использованием
    pool_recycle=300     # Обновляет соединение каждые 5 минут
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# SQL-модель для таблицы articles
class ArticleORM(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    text = Column(String)
    link = Column(String)
    source = Column(String)
    pub_date = Column(DateTime)

app = FastAPI(title="Aggregator Parser Service")
@app.post("/parse", response_model=List[Article])
async def parse_aggregator(urls: List[str]):
    all_articles = []
    print(f"DEBUG: Начинаю обработку URL: {urls}")
    db = SessionLocal()
    try:
        for url in urls:
            print(f"DEBUG: Парсинг RSS: {url}")
            articles = parse_rss(url.strip())
            print(f"DEBUG: Найдено статей: {len(articles)}")
            for art_data in articles:
                print(f"DEBUG: Сохранение в БД: {art_data.title}")
                new_article = ArticleORM(
                    title=art_data.title,
                    text=art_data.text,
                    link=art_data.link,
                    source=art_data.source,
                    pub_date=art_data.pub_date
                )
                db.add(new_article)
                db.commit() # Если виснет здесь — проблема в БД
                db.refresh(new_article)
                
                art_data.id = new_article.id
                
                print(f"DEBUG: Отправка в Kafka: {art_data.id}")
                await send_article_to_kafka(art_data) # Если виснет здесь — проблема в Kafka
                all_articles.append(art_data)
        
        print("DEBUG: Обработка завершена успешно")
        return all_articles
    except Exception as e:
        print(f"DEBUG: ПРОИЗОШЛА ОШИБКА: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()