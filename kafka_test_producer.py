"""
Простой тестовый продьюсер для отправки сообщений в Kafka-топик text_for_sentiment.

Используется для локальной проверки работы сервиса sentiment_analysis.
"""

import json
import time

from confluent_kafka import Producer

from sentiment_analysis.config import get_settings


def delivery_report(err, msg):  # type: ignore[no-untyped-def]
    """Коллбэк о результате доставки сообщения."""

    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(
            f"Record successfully produced to {msg.topic()} "
            f"[{msg.partition()}] at offset {msg.offset()}"
        )


def main() -> None:
    settings = get_settings()
    producer_conf = {"bootstrap.servers": settings.kafka_bootstrap_servers}
    producer = Producer(producer_conf)

    payload = {
        "id": 123,
        "title": "Газпром временно остановил поставки",
        "text": "Газпром временно остановил поставки газа в Европу...",
        "clean_text": "газпром временно остановил поставки газа в европу",
        "tokens": ["газпром", "временно", "остановить", "поставка", "газ", "европа"],
        "source": "ria.ru",
        "pub_date": "2025-02-10T10:00:00Z",
    }

    topic = settings.kafka_topic
    data = json.dumps(payload).encode("utf-8")

    producer.produce(
        topic=topic,
        value=data,
        on_delivery=delivery_report,
    )
    producer.flush()

    # Небольшая пауза, чтобы коллбэк успел отработать
    time.sleep(1)


if __name__ == "__main__":
    main()



