import json
from aiokafka import AIOKafkaProducer
from .config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC

producer = None

async def get_kafka_producer():
    global producer
    if producer is None:
        producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
        await producer.start()
    return producer

async def send_article_to_kafka(article: dict):
    prod = await get_kafka_producer()
    await prod.send_and_wait(KAFKA_TOPIC, json.dumps(article).encode("utf-8"))