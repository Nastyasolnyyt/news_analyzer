import asyncio
from .kafka_consumer import consume_from_kafka

if __name__ == "__main__":
    # Запускаем Kafka consumer для обработки риск-уровня
    asyncio.run(consume_from_kafka())