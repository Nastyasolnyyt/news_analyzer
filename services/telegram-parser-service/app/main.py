# services/telegram-parser/app/main.py
import logging
import asyncio # Добавляем для работы с таймером
from typing import List
from .config import KAFKA_BOOTSTRAP_SERVERS, PARSE_INTERVAL
from fastapi import FastAPI, BackgroundTasks, HTTPException
from sqlalchemy.dialects.postgresql import insert

from .database import SessionLocal, ArticleORM, init_db
from .models import Article as ArticleModel
from .parsers import parse_telegram_channels
from .kafka_producer import send_article_to_kafka

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Parser")

# Функция, которая содержит основную логику парсинга
async def perform_parsing():
    logger.info("Запуск цикла парсинга Telegram...")
    try:
        articles: List[ArticleModel] = await parse_telegram_channels()
        if not articles:
            logger.warning("Статей не найдено")
            return
        
        db = SessionLocal()
        try:
            for article in articles:
                stmt = insert(ArticleORM).values(
                    title=article.title or "Telegram Post",
                    content=article.text,
                    link=article.link,
                    source=article.source,
                    pub_date=article.pub_date
                ).on_conflict_do_nothing(index_elements=['link'])
                
                db.execute(stmt)
                db.commit()

                existing = db.query(ArticleORM).filter(ArticleORM.link == article.link).first()
                if existing:
                    article_dict = {
                        "article_id": existing.id,
                        "title": existing.title,
                        "text": existing.content,
                        "link": existing.link,
                        "source": existing.source,
                        "pub_date": existing.pub_date.isoformat() if existing.pub_date else None
                    }
                    await send_article_to_kafka(article_dict)
        finally:
            db.close()
        logger.info(f"Успешно обработано {len(articles)} статей")
    except Exception as e:
        logger.error(f"Ошибка в процессе парсинга: {e}")

# Фоновая задача с циклом
async def schedule_parsing():
    # Даем сервису немного времени на запуск (например, 10 секунд)
    await asyncio.sleep(PARSE_INTERVAL)
    while True:
        await perform_parsing()
        # 1800 секунд = 30 минут
        logger.info("Следующий парсинг через 30 минут...")
        await asyncio.sleep(1800)

@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized")
    # Запускаем фоновую задачу, не блокируя основной поток FastAPI
    asyncio.create_task(schedule_parsing())

@app.post("/parse_telegram")
async def parse_telegram_endpoint():
    """Ручной запуск парсинга через API (оставляем для тестов)"""
    await perform_parsing()
    return {"status": "started"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "telegram-parser"}