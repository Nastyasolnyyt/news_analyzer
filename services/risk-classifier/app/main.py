import asyncio
from .kafka_worker import consume_from_kafka

if __name__ == "__main__":
    # Запускаем Kafka consumer для обработки риск-анализа
    asyncio.run(consume_from_kafka())