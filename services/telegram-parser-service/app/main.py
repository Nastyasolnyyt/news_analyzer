# services/telegram-parser/app/main.py
import logging
from typing import List
from fastapi import FastAPI, BackgroundTasks, HTTPException
from sqlalchemy.dialects.postgresql import insert

from .database import SessionLocal, ArticleORM, init_db
from .models import Article as ArticleModel
from .parsers import parse_telegram_channels
from .kafka_producer import send_article_to_kafka

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Parser")

@app.on_event("startup")
async def startup_event():
    """Инициализация БД при старте"""
    init_db()
    logger.info("Database initialized")

@app.post("/parse_telegram", response_model=List[dict])
async def parse_telegram_endpoint(background_tasks: BackgroundTasks):
    """
    Запускает парсинг настроенных Telegram-каналов.
    Возвращает список обработанных статей.
    """
    logger.info("Запуск парсинга Telegram...")
    
    try:
        # 1. Парсим каналы (это async функция!)
        articles: List[ArticleModel] = await parse_telegram_channels()
        
        if not articles:
            logger.warning(" Не найдено статей для парсинга")
            return []
        
        logger.info(f"Получено {len(articles)} статей из Telegram")
        
        # 2. Обрабатываем каждую статью
        processed = []
        db = SessionLocal()
        
        try:
            for article in articles:
                # UPSERT: если статья с таким link уже есть — пропускаем
                stmt = insert(ArticleORM).values(
                    title=article.title or "Telegram Post",
                    content=article.text,
                    link=article.link,
                    source=article.source,
                    pub_date=article.pub_date
                ).on_conflict_do_nothing(index_elements=['link'])
                
                db.execute(stmt)
                db.commit()
                
                # Получаем ID статьи (для отправки в Kafka)
                existing = db.query(ArticleORM).filter(
                    ArticleORM.link == article.link
                ).first()
                
                if existing:
                    # Формируем сообщение для Kafka
                    article_dict = {
                        "article_id": existing.id,
                        "title": existing.title,
                        "text": existing.content,
                        "link": existing.link,
                        "source": existing.source,
                        "pub_date": existing.pub_date.isoformat() if existing.pub_date else None
                    }
                    
                    # Отправляем в Kafka (можно в background, если много статей)
                    await send_article_to_kafka(article_dict)
                    
                    processed.append({
                        "id": existing.id,
                        "title": article.title,
                        "link": article.link,
                        "source": article.source
                    })
            
            logger.info(f"Обработано {len(processed)} статей")
            return processed
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f" Ошибка парсинга: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Parse error: {str(e)}")

@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {"status": "ok", "service": "telegram-parser"}