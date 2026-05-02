# app/kafka_producer.py

import asyncio
import json
from aiokafka import AIOKafkaProducer
from .config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC
from .models import Article

KAFKA_SEND_TIMEOUT = 15  # секунд


async def send_article_to_kafka(article: Article):
    """
    Создаёт producer, отправляет одну статью и сразу закрывает.
    Глобальный producer убран — он зависал после первого цикла,
    блокируя все последующие запуски APScheduler.
    """
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        request_timeout_ms=10_000,
    )
    try:
        await asyncio.wait_for(producer.start(), timeout=10)
    except Exception as e:
        print(f"Failed to start Kafka producer: {e}")
        return

    message = {
        "id": article.id,
        "article_id": article.id,
        "title": article.title,
        "text": article.text,
        "link": article.link,
        "source": article.source,
    }

    try:
        value = json.dumps(message, ensure_ascii=False).encode("utf-8")
        await asyncio.wait_for(
            producer.send_and_wait(KAFKA_TOPIC, value),
            timeout=KAFKA_SEND_TIMEOUT,
        )
    except asyncio.TimeoutError:
        print(f"Timeout sending article {article.id} to Kafka")
    except Exception as e:
        print(f"Failed to send article {article.id} to Kafka: {e}")
    finally:
        try:
            await producer.stop()
        except Exception:
            pass