"""
Notification Consumer Main - запуск фонового сервиса для отправки уведомлений
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

from src.services.notification_consumer import run_notification_consumer

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция"""

    # Получаем конфигурацию из переменных окружения
    database_url = os.getenv("DATABASE_URL")
    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_input_topic = os.getenv("KAFKA_INPUT_TOPIC", "articles_analyzed")
    kafka_group_id = os.getenv("KAFKA_NOTIFICATION_GROUP_ID", "notifications-sender-group")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    logger.info("=" * 60)
    logger.info("NOTIFICATION CONSUMER STARTED")
    logger.info("=" * 60)
    logger.info(f"Kafka Servers: {kafka_bootstrap_servers}")
    logger.info(f"Input Topic: {kafka_input_topic}")
    logger.info(f"Group ID: {kafka_group_id}")
    logger.info(f"Database: {database_url[:30]}...")
    logger.info("=" * 60)

    try:
        await run_notification_consumer(
            database_url=database_url,
            kafka_bootstrap_servers=kafka_bootstrap_servers,
            kafka_input_topic=kafka_input_topic,
            kafka_group_id=kafka_group_id,
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
