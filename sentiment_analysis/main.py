import logging
import sys

from dotenv import load_dotenv
from sqlalchemy import text

from .config import get_settings
from .consumer import run_consumer
from .db import engine
from .sentiment_model import init_model


def setup_logging() -> None:
    """Настраивает базовое логирование для сервиса."""

    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def _check_database_connection() -> None:
    """Пробная проверка соединения с БД."""

    logger = logging.getLogger(__name__)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connection check succeeded")
    except Exception as exc:  # noqa: BLE001
        logger.error("Database connection check failed: %s", exc, exc_info=True)
        raise


def main() -> None:
    """Точка входа микросервиса sentiment_analysis."""

    # Подхватываем .env при наличии
    load_dotenv()

    setup_logging()
    logger = logging.getLogger(__name__)

    settings = get_settings()
    logger.info("Starting sentiment_analysis service with settings: %s", settings)

    # Инициализируем модель и проверяем соединение с БД на старте
    init_model()
    _check_database_connection()

    # Запускаем бесконечный цикл чтения из Kafka и записи в БД
    run_consumer()


if __name__ == "__main__":
    main()




