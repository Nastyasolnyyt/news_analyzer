from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.config import settings
from app.kafka_consumer import run_kafka_consumer
from app.redis_storage import RedisGraphStorage
from app.rest_api import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage = RedisGraphStorage()
    await storage.connect()
    app.state.storage = storage
    consumer_task = asyncio.create_task(run_kafka_consumer(storage))
    logger.info("Kafka consumer started in background")
    try:
        yield
    finally:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
        await storage.close()
        logger.info("Application shutdown complete")


app = FastAPI(title="Knowledge Graph API", lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.rest_host, port=settings.rest_port, log_level="info")
