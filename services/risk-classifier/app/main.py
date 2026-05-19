"""
services/risk-classifier/app/main.py
ИСПРАВЛЕННЫЙ: запускает Kafka consumer с HF классификатором
"""
import asyncio
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импортируем worker
from app.kafka_worker import main as run_consumer
from app.storage import init_db

async def main():
    """Основная точка входа"""
    logger.info("Запуск risk-classifier (Hugging Face модель)...")
    init_db()
    try:
        await run_consumer()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
