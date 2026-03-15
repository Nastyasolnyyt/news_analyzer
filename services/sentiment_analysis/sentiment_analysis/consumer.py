import json
import logging
from typing import Any, Dict, Optional

from confluent_kafka import Consumer, KafkaError, Message

from .config import get_settings
from .db import get_session
from .models import Sentiment
from .sentiment_model import analyze_sentiment


logger = logging.getLogger(__name__)


def _build_consumer() -> Consumer:
    """Создает и настраивает Kafka-консьюмера."""

    settings = get_settings()
    config = {
        "bootstrap.servers": settings.kafka_bootstrap_servers,
        "group.id": settings.kafka_group_id,
        "auto.offset.reset": settings.kafka_auto_offset_reset,
        "enable.auto.commit": settings.kafka_enable_auto_commit,
    }
    consumer = Consumer(config)
    consumer.subscribe([settings.kafka_topic])

    logger.info(
        "Kafka consumer subscribed",
        extra={
            "topic": settings.kafka_topic,
            "group_id": settings.kafka_group_id,
            "bootstrap_servers": settings.kafka_bootstrap_servers,
        },
    )
    return consumer


def _parse_message(msg: Message) -> Optional[Dict[str, Any]]:
    """Парсит JSON-сообщение из Kafka."""

    try:
        value_bytes = msg.value()
        if value_bytes is None:
            logger.warning("Received message with empty value")
            return None
        return json.loads(value_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        logger.error("Failed to decode JSON from Kafka message: %s", exc)
    except UnicodeDecodeError as exc:
        logger.error("Failed to decode bytes from Kafka message: %s", exc)
    return None


def _extract_text(payload: Dict[str, Any]) -> Optional[str]:
    """Извлекает текст для анализа из полезной нагрузки."""

    text_fields = [
        payload.get("clean_text"),
        payload.get("text"),
        payload.get("title"),
    ]
    for field in text_fields:
        if isinstance(field, str) and field.strip():
            return field
    return None


def _save_sentiment(
    article_id: int,
    sentiment_label: str,
    confidence_score: float,
) -> None:
    """Сохраняет результат анализа тональности в БД."""

    from sqlalchemy.exc import SQLAlchemyError

    try:
        with get_session() as session:
            sentiment = Sentiment(
                article_id=article_id,
                sentiment_label=sentiment_label,
                confidence_score=confidence_score,
            )
            session.add(sentiment)
    except SQLAlchemyError as exc:
        logger.error(
            "Failed to save sentiment to database: %s",
            exc,
            exc_info=True,
        )
        raise


def process_message(msg: Message, commit_success: bool = True) -> None:
    """
    Обрабатывает одно сообщение Kafka:
    - парсит JSON,
    - анализирует тональность,
    - сохраняет результат в БД.
    """

    payload = _parse_message(msg)
    if not payload:
        return

    article_id = payload.get("id")
    if article_id is None:
        logger.warning("Message without 'id' field: %s", payload)
        return

    text = _extract_text(payload)
    if not text:
        logger.warning("No text fields found for article_id=%s", article_id)
        return

    try:
        sentiment_label, confidence_score = analyze_sentiment(text)
        _save_sentiment(
            article_id=int(article_id),
            sentiment_label=sentiment_label,
            confidence_score=confidence_score,
        )
        logger.info(
            "Sentiment saved",
            extra={
                "article_id": article_id,
                "sentiment_label": sentiment_label,
                "confidence_score": confidence_score,
            },
        )
    except Exception as exc:
        # Логируем, но не роняем сервис
        logger.error(
            "Failed to process message for article_id=%s: %s",
            article_id,
            exc,
            exc_info=True,
        )
        # commit_success флаг оставлен на будущее для стратегии коммитов
        if not commit_success:
            raise


def run_consumer() -> None:
    """Запускает основной цикл Kafka-консьюмера."""

    consumer = _build_consumer()
    settings = get_settings()

    logger.info("Starting Kafka consumer loop for topic '%s'", settings.kafka_topic)

    try:
        while True:
            msg: Message | None = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # Конец раздела — не ошибка
                    continue
                logger.error("Kafka error: %s", msg.error())
                continue

            process_message(msg)

            # Мы используем ручные коммиты только если авто-коммит выключен
            if not settings.kafka_enable_auto_commit:
                try:
                    consumer.commit(msg)
                except KafkaError as exc:
                    logger.error("Failed to commit Kafka offset: %s", exc)
    except KeyboardInterrupt:
        logger.info("Kafka consumer interrupted by user, shutting down...")
    finally:
        consumer.close()
        logger.info("Kafka consumer closed")



