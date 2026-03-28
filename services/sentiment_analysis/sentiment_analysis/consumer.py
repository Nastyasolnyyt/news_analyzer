import json
import logging
from kafka import KafkaConsumer
from sqlalchemy.dialects.postgresql import insert
from .db import get_session
from .models import PostAnalysis
from .sentiment_model import analyze_sentiment
from .config import get_settings

logger = logging.getLogger(__name__)

# Маппинг текста в числа для БД
SENTIMENT_MAP = {
    "positive": 1.0,
    "neutral": 0.0,
    "negative": -1.0
}

def process_message(msg):
    try:
        # msg.value is already bytes, deserialize it
        if isinstance(msg.value, bytes):
            value = msg.value.decode("utf-8")
        else:
            value = msg.value
        data = json.loads(value)
        article_id = data.get("article_id")
        text_to_analyze = data.get("text")

        if not article_id or not text_to_analyze:
            return

        # Обрезаем текст до 512 символов (безопасный лимит для RuBERT)
        text_to_analyze = text_to_analyze[:512]

        # 1. Анализ
        label, score = analyze_sentiment(text_to_analyze)
        numeric_tonality = SENTIMENT_MAP.get(label, 0.0)

        # 2. UPSERT в общую таблицу анализа
        with get_session() as session:
            stmt = insert(PostAnalysis).values(
                post_id=article_id,          
                tonality=numeric_tonality,   
                confidence=score,
                sentiment_label=label
            ).on_conflict_do_update(
                index_elements=['post_id'],   
                set_={
                    'tonality': numeric_tonality,
                    'confidence': numeric_tonality,  
                    'sentiment_label': label
                }
            )
            session.execute(stmt)
            session.commit()
            
        logger.info(f"Analyzed article {article_id}: {label} ({score})")

    except Exception as exc:
        logger.error(f"Failed to process sentiment for article: {exc}")


def run_consumer():
    """Main Kafka consumer loop for processing sentiment analysis messages."""
    settings = get_settings()
    logger.info(f"Starting Kafka consumer for topic: {settings.kafka_topic}")
    
    consumer = KafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="sentiment-analysis-group",
        auto_offset_reset="earliest",
        value_deserializer=lambda m: m,
    )
    
    try:
        for message in consumer:
            try:
                process_message(message)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                continue
    except KeyboardInterrupt:
        logger.info("Shutting down consumer")
    finally:
        consumer.close()