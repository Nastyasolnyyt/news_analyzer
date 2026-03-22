import json
import logging
from sqlalchemy.dialects.postgresql import insert
from .db import get_session
from .models import PostAnalysis
from .sentiment_model import analyze_sentiment

logger = logging.getLogger(__name__)

# Маппинг текста в числа для БД
SENTIMENT_MAP = {
    "positive": 1.0,
    "neutral": 0.0,
    "negative": -1.0
}

def process_message(msg):
    try:
        data = json.loads(msg.value().decode("utf-8"))
        article_id = data.get("article_id")
        text_to_analyze = data.get("text")

        if not article_id or not text_to_analyze:
            return

        # 1. Анализ
        label, score = analyze_sentiment(text_to_analyze)
        numeric_tonality = SENTIMENT_MAP.get(label, 0.0)

        # 2. UPSERT в общую таблицу анализа
        with get_session() as session:
            stmt = insert(PostAnalysis).values(
                post_id=article_id,
                tonality=numeric_tonality,
                confidence=score,
                emotion=0.0, # Если модель не выдает эмоции, ставим 0
                relevance=0.0
            ).on_conflict_do_update(
                index_elements=['post_id'],
                set_={
                    'tonality': numeric_tonality,
                    'confidence': score
                }
            )
            session.execute(stmt)
            session.commit()
            
        logger.info(f"Analyzed article {article_id}: {label} ({score})")

    except Exception as exc:
        logger.error(f"Failed to process sentiment for article: {exc}")