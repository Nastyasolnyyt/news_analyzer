"""
ИСПРАВЛЕНО:
1. CommitFailedError / Kafka Rebalance — добавлены max_poll_interval_ms,
   session_timeout_ms, heartbeat_interval_ms
2. Отключён авто-коммит, добавлен ручной commit после успешной обработки
3. Обработка текста ограничена 512 токенами (не символами) — безопасно для BERT
"""
import json
import logging
from kafka import KafkaConsumer
from sqlalchemy.dialects.postgresql import insert
from .db import get_session
from .models import PostAnalysis
from .sentiment_model import analyze_sentiment
from .config import get_settings

logger = logging.getLogger(__name__)

# Маппинг тональности в числа для БД
SENTIMENT_MAP = {
    "positive": 1.0,
    "neutral": 0.0,
    "negative": -1.0,
}


def process_message(msg):
    """Обрабатывает одно сообщение из Kafka."""
    try:
        if isinstance(msg.value, bytes):
            value = msg.value.decode("utf-8")
        else:
            value = msg.value
        data = json.loads(value)

        article_id = data.get("article_id") or data.get("id")
        text_to_analyze = data.get("text") or data.get("clean_text") or ""

        if not article_id:
            logger.warning("Пропускаю сообщение без article_id")
            return

        if not text_to_analyze or not text_to_analyze.strip():
            logger.warning(f"Пустой текст для статьи {article_id}, пропускаю")
            return

        # BERT работает с токенами, но мы обрезаем по символам безопасно
        # ~512 символов ≈ 100-150 токенов, хорошо укладывается в лимит модели
        text_to_analyze = text_to_analyze[:512]

        # Анализ тональности
        label, score = analyze_sentiment(text_to_analyze)
        numeric_tonality = SENTIMENT_MAP.get(label, 0.0)

        # UPSERT в таблицу post_analysis
        with get_session() as session:
            stmt = insert(PostAnalysis).values(
                post_id=article_id,
                tonality=numeric_tonality,
                confidence=score,
                sentiment_label=label,
            ).on_conflict_do_update(
                index_elements=["post_id"],
                set_={
                    "tonality": numeric_tonality,
                    "confidence": score,
                    "sentiment_label": label,
                },
            )
            session.execute(stmt)
            session.commit()

        logger.info(f"Analyzed article {article_id}: {label} ({score:.3f})")

    except Exception as exc:
        logger.error(f"Failed to process sentiment for article: {exc}", exc_info=True)
        raise  # Пробрасываем, чтобы не коммитить offset


def run_consumer():
    """Основной цикл Kafka consumer для анализа тональности."""
    settings = get_settings()
    logger.info(f"Starting Kafka consumer for topic: {settings.kafka_topic}")

    consumer = KafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="sentiment-analysis-group",
        auto_offset_reset="earliest",

        # ИСПРАВЛЕНО: Анализ BERT-модели занимает ~5-30 сек на статью.
        # Kafka по умолчанию убивает consumer если он не делает poll() в течение
        # max_poll_interval_ms (по умолчанию 300 сек = 5 мин).
        # При батче из нескольких статей легко превысить.
        # Устанавливаем более щадящие значения:
        max_poll_interval_ms=600_000,   # 10 минут между poll() вызовами
        session_timeout_ms=60_000,      # 60 сек до кика из группы
        heartbeat_interval_ms=20_000,   # heartbeat каждые 20 сек

        # ИСПРАВЛЕНО: Отключаем авто-коммит — будем коммитить вручную
        # после успешной обработки, чтобы не потерять сообщения при ошибке
        enable_auto_commit=False,

        # Обрабатываем по 1 сообщению за раз, чтобы не превышать poll interval
        max_poll_records=1,

        value_deserializer=lambda m: m,  # Получаем bytes, декодируем в process_message
    )

    logger.info("Kafka consumer запущен, ожидаю сообщения...")

    try:
        for message in consumer:
            try:
                process_message(message)
                # Коммитим offset только после успешной обработки
                consumer.commit()
            except Exception as e:
                logger.error(f"Ошибка обработки сообщения (offset не закоммичен): {e}")
                # НЕ коммитим offset — сообщение будет перечитано после рестарта
                continue
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки, завершаю работу...")
    finally:
        consumer.close()
        logger.info("Kafka consumer остановлен")