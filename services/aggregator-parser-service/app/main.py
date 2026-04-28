# aggregator-parser/app/main.py
from sqlalchemy.dialects.postgresql import insert
from fastapi import FastAPI, HTTPException
from typing import List
import asyncio
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from .database import SessionLocal, ArticleORM
from .models import Article
from .parsers import parse_rss
from .kafka_producer import send_article_to_kafka

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

scheduler = BackgroundScheduler()

RSS_URLS = ["https://www.vedomosti.ru/rss/news.xml"]


async def run_parsing_logic(urls: List[str]):
    """
    Основная логика парсинга — вызывается и из планировщика, и из API.
    """
    all_articles = []
    db = SessionLocal()
    try:
        for url in urls:
            articles = parse_rss(url.strip())
            logger.info(f"Получено {len(articles)} статей с {url}")

            for art_data in articles:
                stmt = insert(ArticleORM).values(
                    title=art_data.title,
                    content=art_data.text,
                    link=art_data.link,
                    source=art_data.source,
                    pub_date=art_data.pub_date
                )
                stmt = stmt.on_conflict_do_nothing(index_elements=['link'])
                db.execute(stmt)
                db.commit()

                existing = db.query(ArticleORM).filter(
                    ArticleORM.link == art_data.link
                ).first()

                if existing:
                    art_data.id = existing.id
                    await send_article_to_kafka(art_data)
                    all_articles.append(art_data)

        logger.info(f"Парсинг завершён. Обработано статей: {len(all_articles)}")
        return all_articles

    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при парсинге: {e}", exc_info=True)
        return []
    finally:
        db.close()


def scheduled_parse_job():
    """
    Обёртка для APScheduler.
    ИСПРАВЛЕНО: используем asyncio.run() вместо get_event_loop(),
    потому что APScheduler запускает задачу в отдельном потоке,
    где нет работающего event loop FastAPI.
    """
    logger.info(f"[{datetime.now()}] Запуск автоматического сбора новостей...")
    try:
        asyncio.run(run_parsing_logic(RSS_URLS))
    except Exception as e:
        logger.error(f"Ошибка в scheduled_parse_job: {e}", exc_info=True)


@app.on_event("startup")
async def start_scheduler():
    """
    Запускается при старте сервера.
    ИСПРАВЛЕНО: next_run_time=datetime.now() — первый парсинг сразу при старте,
    затем каждые 30 минут.
    """
    scheduler.add_job(
        scheduled_parse_job,
        'interval',
        minutes=30,
        id='rss_parse_task',
        next_run_time=datetime.now()  # сразу запускаем при старте
    )
    scheduler.start()
    jobs = scheduler.get_jobs()
    logger.info(f"Планировщик запущен. Активных задач: {len(jobs)}")
    for job in jobs:
        logger.info(f"  Задача: {job.id}, следующий запуск: {job.next_run_time}")


@app.on_event("shutdown")
async def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("Планировщик остановлен")


@app.post("/parse", response_model=List[Article])
async def parse_endpoint(urls: List[str]):
    """
    Ручной запуск парсинга через API.
    """
    articles = await run_parsing_logic(urls)
    if not articles and urls:
        raise HTTPException(
            status_code=500,
            detail="Ошибка при парсинге или нет новых данных"
        )
    return articles


@app.get("/health")
async def health():
    jobs = scheduler.get_jobs()
    next_run = jobs[0].next_run_time if jobs else None
    return {
        "status": "ok",
        "scheduler_running": scheduler.running,
        "next_parse": str(next_run)
    }