# aggregator-parser/app/main.py
from sqlalchemy.dialects.postgresql import insert
from fastapi import FastAPI, HTTPException
from typing import List
import asyncio

# Добавляем планировщик
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from .database import SessionLocal, ArticleORM
from .models import Article
from .parsers import parse_rss
from .kafka_producer import send_article_to_kafka

app = FastAPI()

# Создаем объект планировщика
scheduler = BackgroundScheduler()

# Список URL для автоматического парсинга
RSS_URLS = ["https://www.vedomosti.ru/rss/news.xml"]

async def run_parsing_logic(urls: List[str]):
    """
    Вынесенная логика парсинга, которую можно вызвать и из API, и из планировщика.
    """
    all_articles = []
    db = SessionLocal()
    try:
        for url in urls:
            articles = parse_rss(url.strip())
            for art_data in articles:
                # 1. Готовим UPSERT
                stmt = insert(ArticleORM).values(
                    title=art_data.title,
                    content=art_data.text,
                    link=art_data.link,
                    source=art_data.source,
                    pub_date=art_data.pub_date
                )
                
                # Если ссылка уже есть, ничего не меняем
                stmt = stmt.on_conflict_do_nothing(index_elements=['link'])
                db.execute(stmt)
                db.commit()

                # 2. Достаем актуальный ID из базы
                existing = db.query(ArticleORM).filter(ArticleORM.link == art_data.link).first()
                
                if existing:
                    art_data.id = existing.id
                    # 3. ОТПРАВКА В KAFKA
                    await send_article_to_kafka(art_data)
                    all_articles.append(art_data)
        return all_articles
    except Exception as e:
        db.rollback()
        print(f"Ошибка при автоматическом парсинге: {e}")
        return []
    finally:
        db.close()

def scheduled_parse_job():
    """
    Обертка для планировщика, чтобы запускать асинхронную функцию в синхронном окружении.
    """
    print(f"[{datetime.now()}] Запуск автоматического сбора новостей...")
    # Используем существующий цикл событий или создаем новый для запуска async логики
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(run_parsing_logic(RSS_URLS))
        else:
            loop.run_until_complete(run_parsing_logic(RSS_URLS))
    except RuntimeError:
        asyncio.run(run_parsing_logic(RSS_URLS))

@app.on_event("startup")
async def start_scheduler():
    """
    Запускается при старте сервера.
    """
    # Добавляем задачу: каждые 30 минут
    scheduler.add_job(scheduled_parse_job, 'interval', minutes=30, id='rss_parse_task')
    scheduler.start()
    print("Планировщик запущен. Парсинг будет происходить каждые 30 минут.")

@app.on_event("shutdown")
async def shutdown_scheduler():
    """
    Остановка планировщика при выключении сервера.
    """
    scheduler.shutdown()

@app.post("/parse", response_model=List[Article])
async def parse_endpoint(urls: List[str]):
    """
    Ручной запуск парсинга через API (оставляем для тестов).
    """
    articles = await run_parsing_logic(urls)
    if not articles and urls:
        raise HTTPException(status_code=500, detail="Ошибка при парсинге или нет новых данных")
    return articles