# app/kafka_producer.py

import asyncio
from aiokafka import AIOKafkaProducer
from .config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC
# Добавляем импорт модели Article, как мы это делали в предыдущем шаге
from .models import Article 

producer = None

async def get_kafka_producer():
    global producer
    if producer is None:
        # Добавляем таймаут для подключения, удалив connection_timeout_ms
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            request_timeout_ms=10000  # 10 секунд — таймаут на отправку
        )
        try:
            await producer.start()
        except Exception as e:
            print(f"Failed to start Kafka producer: {e}")
            raise
    return producer

async def send_article_to_kafka(article: Article):
    prod = await get_kafka_producer()
    
    # Используем model_dump_json() для сериализации datetime
    json_str = article.model_dump_json(exclude_none=True) 
    
    try:
        # УБЕДИТЕСЬ, ЧТО ЗДЕСЬ НЕТ timeout=...
        await prod.send_and_wait(KAFKA_TOPIC, json_str.encode("utf-8")) 
    except Exception as e:
        print(f"Failed to send article to Kafka: {e}")