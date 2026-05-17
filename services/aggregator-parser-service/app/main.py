# aggregator-parser/app/main.py
from sqlalchemy.dialects.postgresql import insert
from fastapi import FastAPI, HTTPException
from typing import List
import asyncio
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from .database import SessionLocal, ArticleORM, init_db
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
    Kafka-отправка ограничена таймаутом на уровне producer,
    чтобы зависание одного сообщения не блокировало весь цикл.
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
                    pub_date=art_data.pub_date,
                )
                stmt = stmt.on_conflict_do_nothing(index_elements=["link"])
                db.execute(stmt)
                db.commit()

                existing = (
                    db.query(ArticleORM)
                    .filter(ArticleORM.link == art_data.link)
                    .first()
                )

                if existing:
                    art_data.id = existing.id
                    # Каждая отправка имеет собственный таймаут внутри producer
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
    APScheduler запускает задачу в отдельном потоке без event loop,
    поэтому используем asyncio.run() — он создаёт свежий loop и
    гарантированно завершает его, не оставляя висящих корутин.
    """
    logger.info(f"[{datetime.now()}] Запуск автоматического сбора новостей...")
    try:
        # asyncio.run() создаёт новый event loop для каждого вызова —
        # именно это нужно, чтобы предыдущий зависший цикл не мешал следующему.
        asyncio.run(run_parsing_logic(RSS_URLS))
    except Exception as e:
        logger.error(f"Ошибка в scheduled_parse_job: {e}", exc_info=True)


@app.on_event("startup")
async def start_scheduler():
    """
    Запускается при старте сервера.
    max_instances=1 оставляем — дублирование не нужно.
    misfire_grace_time=None означает «запустить, даже если опоздал».
    """
    # Инициализируем БД и добавляем constraint если нужно
    init_db()
    
    scheduler.add_job(
        scheduled_parse_job,
        "interval",
        minutes=30,
        id="rss_parse_task",
        max_instances=1,
        misfire_grace_time=None,      # не пропускать пропущенные запуски
        next_run_time=datetime.now(),  # первый запуск сразу при старте
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
    """Ручной запуск парсинга через API."""
    articles = await run_parsing_logic(urls)
    if not articles and urls:
        raise HTTPException(
            status_code=500,
            detail="Ошибка при парсинге или нет новых данных",
        )
    return articles


@app.get("/health")
async def health():
    jobs = scheduler.get_jobs()
    next_run = jobs[0].next_run_time if jobs else None
    return {
        "status": "ok",
        "scheduler_running": scheduler.running,
        "next_parse": str(next_run),
    }