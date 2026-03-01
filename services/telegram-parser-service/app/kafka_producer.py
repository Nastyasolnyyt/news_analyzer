import json
from aiokafka import AIOKafkaProducer
from .config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC
from datetime import datetime
import logging

producer = None

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: serialize_datetime(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime(item) for item in obj]
    else:
        return obj

async def get_kafka_producer():
    global producer
    if producer is None:
        producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
        await producer.start()
    return producer

async def send_article_to_kafka(article: dict):
    prod = await get_kafka_producer()
    
    # Преобразуем datetime в ISO строки рекурсивно
    processed_article = serialize_datetime(article)
    
    # Теперь сериализуем в JSON
    json_str = json.dumps(processed_article, ensure_ascii=False)
    
    await prod.send_and_wait(KAFKA_TOPIC, json_str.encode("utf-8"))