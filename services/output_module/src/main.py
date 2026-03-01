from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from loguru import logger
from src.core.logger.default import setup_uvicorn_loggers
from src.core.modules.cache import CacheProvider
from src.core.modules.config import ConfigProvider
from src.core.modules.db import DBProvider
from src.core.modules.service import ServiceProvider
from src.infrastructure.postgres.connection import DATABASE_URL
from src.presentation.api.setup import setup_routes
from starlette.middleware.cors import CORSMiddleware


setup_uvicorn_loggers()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Сервер запускается...")
    logger.info("Сервер запущен")
    yield
    logger.info("Остановка работы...")
    logger.info("Работа сервера остановлена...")


container = make_async_container(
    DBProvider(DATABASE_URL),
    ConfigProvider(),
    ServiceProvider(),
    CacheProvider(),
    FastapiProvider(),
)

app = FastAPI(
    title="Output Module Back",
    description="Output Module Back",
    version="1.0.0",
    lifespan=lifespan,
)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_dishka(app=app, container=container)
setup_routes(app)
